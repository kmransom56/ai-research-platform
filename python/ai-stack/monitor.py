#!/usr/bin/env python3
"""
Advanced AI Stack Monitoring System
Monitors system resources and AI service health
"""

import psutil
import time
import json
import requests
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AIStackMonitor:
    """Monitor for Advanced AI Stack services"""
    
    def __init__(self, gateway_url: str = "http://localhost:9000"):
        self.gateway_url = gateway_url
        self.backends = {
            'reasoning': 'http://localhost:8000',
            'general': 'http://localhost:8001', 
            'coding': 'http://localhost:8002',
            'creative': 'http://localhost:5001',
            'advanced': 'http://localhost:5000'
        }
        
        # Try to detect GPU
        self.has_gpu = self._detect_gpu()
        if self.has_gpu:
            try:
                import nvidia_ml_py3 as nvml
                nvml.nvmlInit()
                self.nvml = nvml
                self.gpu_handle = nvml.nvmlDeviceGetHandleByIndex(0)
                logger.info("GPU monitoring initialized")
            except Exception as e:
                logger.warning(f"Could not initialize GPU monitoring: {e}")
                self.has_gpu = False
    
    def _detect_gpu(self) -> bool:
        """Detect if GPU is available"""
        try:
            import nvidia_ml_py3 as nvml
            nvml.nvmlInit()
            return True
        except:
            return False
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        stats = {
            "timestamp": datetime.now().isoformat(),
            "cpu": {
                "percent": psutil.cpu_percent(interval=1),
                "count": psutil.cpu_count(),
                "frequency": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            },
            "memory": {
                "total_gb": round(psutil.virtual_memory().total / 1024**3, 2),
                "used_gb": round(psutil.virtual_memory().used / 1024**3, 2),
                "available_gb": round(psutil.virtual_memory().available / 1024**3, 2),
                "percent": psutil.virtual_memory().percent
            },
            "disk": {
                "total_gb": round(psutil.disk_usage('/').total / 1024**3, 2),
                "used_gb": round(psutil.disk_usage('/').used / 1024**3, 2),
                "free_gb": round(psutil.disk_usage('/').free / 1024**3, 2),
                "percent": psutil.disk_usage('/').percent
            }
        }
        
        # Add GPU stats if available
        if self.has_gpu and hasattr(self, 'nvml'):
            try:
                gpu_mem = self.nvml.nvmlDeviceGetMemoryInfo(self.gpu_handle)
                gpu_util = self.nvml.nvmlDeviceGetUtilizationRates(self.gpu_handle)
                gpu_temp = self.nvml.nvmlDeviceGetTemperature(self.gpu_handle, self.nvml.NVML_TEMPERATURE_GPU)
                
                stats["gpu"] = {
                    "memory_total_gb": round(gpu_mem.total / 1024**3, 2),
                    "memory_used_gb": round(gpu_mem.used / 1024**3, 2),
                    "memory_free_gb": round(gpu_mem.free / 1024**3, 2),
                    "memory_percent": round((gpu_mem.used / gpu_mem.total) * 100, 2),
                    "utilization_percent": gpu_util.gpu,
                    "memory_utilization_percent": gpu_util.memory,
                    "temperature_c": gpu_temp
                }
            except Exception as e:
                stats["gpu"] = {"error": str(e)}
        else:
            stats["gpu"] = {"available": False}
        
        return stats
    
    def check_service_health(self, url: str, timeout: int = 5) -> Dict[str, Any]:
        """Check health of a single service"""
        health_endpoints = ['/health', '/v1/models', '/api/v1/info', '/']
        
        for endpoint in health_endpoints:
            try:
                response = requests.get(f"{url}{endpoint}", timeout=timeout)
                return {
                    "status": "online",
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                    "status_code": response.status_code,
                    "endpoint": endpoint
                }
            except requests.exceptions.ConnectionError:
                continue
            except requests.exceptions.Timeout:
                return {
                    "status": "timeout",
                    "endpoint": endpoint,
                    "timeout": timeout
                }
            except Exception as e:
                return {
                    "status": "error",
                    "error": str(e),
                    "endpoint": endpoint
                }
        
        return {
            "status": "offline",
            "message": "All health endpoints failed"
        }
    
    def get_ai_services_health(self) -> Dict[str, Any]:
        """Check health of all AI services"""
        services_health = {}
        
        # Check gateway
        services_health["gateway"] = self.check_service_health(self.gateway_url)
        
        # Check individual backends
        for name, url in self.backends.items():
            services_health[name] = self.check_service_health(url)
        
        # Get overall gateway health if available
        try:
            response = requests.get(f"{self.gateway_url}/health", timeout=10)
            if response.status_code == 200:
                gateway_health = response.json()
                services_health["gateway_detailed"] = gateway_health
        except:
            pass
        
        return services_health
    
    def get_process_info(self) -> Dict[str, Any]:
        """Get information about relevant processes"""
        processes = {}
        
        # Look for AI-related processes
        ai_processes = ["vllm", "koboldcpp", "server.py", "api_gateway.py"]
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_info', 'cpu_percent']):
            try:
                if any(keyword in ' '.join(proc.info['cmdline'] or []).lower() 
                      for keyword in ai_processes):
                    processes[proc.info['pid']] = {
                        "name": proc.info['name'],
                        "cmdline": proc.info['cmdline'],
                        "memory_mb": round(proc.info['memory_info'].rss / 1024**2, 2),
                        "cpu_percent": proc.info['cpu_percent']
                    }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return processes
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive monitoring report"""
        return {
            "system": self.get_system_stats(),
            "ai_services": self.get_ai_services_health(),
            "processes": self.get_process_info(),
            "summary": self._generate_summary()
        }
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary of system health"""
        try:
            system_stats = self.get_system_stats()
            ai_health = self.get_ai_services_health()
            
            # Count online services
            online_services = sum(1 for service in ai_health.values() 
                                if isinstance(service, dict) and service.get('status') == 'online')
            total_services = len(ai_health)
            
            # Determine overall status
            if online_services == 0:
                overall_status = "critical"
            elif online_services < total_services:
                overall_status = "warning"
            else:
                overall_status = "healthy"
            
            return {
                "overall_status": overall_status,
                "services_online": online_services,
                "services_total": total_services,
                "cpu_usage": system_stats["cpu"]["percent"],
                "memory_usage": system_stats["memory"]["percent"],
                "gpu_available": system_stats["gpu"]["available"] if "available" in system_stats["gpu"] else True,
                "gpu_memory_usage": system_stats["gpu"].get("memory_percent", 0),
                "timestamp": system_stats["timestamp"]
            }
        except Exception as e:
            return {"error": str(e), "overall_status": "error"}
    
    def save_report(self, report: Dict[str, Any], filepath: Optional[str] = None) -> str:
        """Save monitoring report to file"""
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"/tmp/ai_stack_monitor_{timestamp}.json"
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        return filepath
    
    def continuous_monitoring(self, interval: int = 30, duration: Optional[int] = None):
        """Run continuous monitoring"""
        logger.info(f"Starting continuous monitoring (interval: {interval}s)")
        
        start_time = time.time()
        
        try:
            while True:
                report = self.generate_report()
                
                # Print summary
                summary = report.get("summary", {})
                print(f"\n{'='*50}")
                print(f"AI Stack Monitor - {summary.get('timestamp', datetime.now().isoformat())}")
                print(f"{'='*50}")
                print(f"Overall Status: {summary.get('overall_status', 'unknown').upper()}")
                print(f"Services: {summary.get('services_online', 0)}/{summary.get('services_total', 0)} online")
                print(f"CPU Usage: {summary.get('cpu_usage', 0):.1f}%")
                print(f"Memory Usage: {summary.get('memory_usage', 0):.1f}%")
                if summary.get('gpu_available'):
                    print(f"GPU Memory Usage: {summary.get('gpu_memory_usage', 0):.1f}%")
                print(f"{'='*50}")
                
                # Save detailed report
                filepath = self.save_report(report)
                logger.info(f"Report saved to: {filepath}")
                
                # Check if duration exceeded
                if duration and (time.time() - start_time) >= duration:
                    logger.info("Monitoring duration completed")
                    break
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")

def main():
    """Main monitoring function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Advanced AI Stack Monitor")
    parser.add_argument("--interval", type=int, default=30, 
                       help="Monitoring interval in seconds (default: 30)")
    parser.add_argument("--duration", type=int, 
                       help="Monitoring duration in seconds (default: unlimited)")
    parser.add_argument("--once", action="store_true", 
                       help="Run once and exit")
    parser.add_argument("--save", type=str, 
                       help="Save report to specific file")
    parser.add_argument("--gateway-url", type=str, default="http://localhost:9000",
                       help="AI Stack Gateway URL")
    
    args = parser.parse_args()
    
    monitor = AIStackMonitor(gateway_url=args.gateway_url)
    
    if args.once:
        # Single report
        report = monitor.generate_report()
        
        if args.save:
            filepath = monitor.save_report(report, args.save)
            print(f"Report saved to: {filepath}")
        else:
            print(json.dumps(report, indent=2))
    else:
        # Continuous monitoring
        monitor.continuous_monitoring(
            interval=args.interval,
            duration=args.duration
        )

if __name__ == "__main__":
    main()