#!/usr/bin/env python3
"""
AI Research Platform Manager with Power Automate Integration
Extended for device management and config backup cleanup
Author: Automated Infrastructure Management
Version: 4.0
"""

import asyncio
import json
import logging
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, TYPE_CHECKING
import subprocess

# Type checking imports
if TYPE_CHECKING:
    import aiohttp
    import psutil


class ServiceType(Enum):
    CORE = "core"
    INFRASTRUCTURE = "infrastructure"
    DOCKER = "docker"
    EXTERNAL = "external"
    DEVICE_MANAGEMENT = "device_management"


class PowerAutomateEventType(Enum):
    PLATFORM_STARTUP = "platform_startup"
    SERVICE_HEALTH = "service_health"
    CONFIG_CLEANUP = "config_cleanup"
    DEVICE_STATUS = "device_status"
    ERROR_ALERT = "error_alert"
    DAILY_REPORT = "daily_report"


@dataclass
class CleanupConfig:
    """Configuration for directory cleanup operations"""
    directory: Path
    retention_days: int = 30
    file_patterns: List[str] = field(default_factory=lambda: ["*.conf", "*.cfg", "*.backup"])
    size_limit_mb: Optional[int] = None
    enabled: bool = True


@dataclass
class PowerAutomateConfig:
    """Power Automate webhook configuration"""
    webhook_url: str
    enabled: bool = True
    timeout: int = 30
    retry_attempts: int = 3
    events: List[PowerAutomateEventType] = field(default_factory=list)


@dataclass
class ServiceConfig:
    name: str
    port: int
    command: Optional[str] = None
    compose_file: Optional[str] = None
    health_path: str = "/"
    host: str = "100.123.10.72"
    service_type: ServiceType = ServiceType.CORE
    use_uv: bool = False
    depends_on: Optional[List[str]] = None
    timeout: int = 30
    power_automate_monitor: bool = False

    def __post_init__(self):
        if self.depends_on is None:
            self.depends_on = []


class PlatformConfig:
    """Enhanced configuration with Power Automate and cleanup settings"""
    
    # Directory configuration
    PLATFORM_DIR = Path("/home/keith/chat-copilot")
    LOGS_DIR = PLATFORM_DIR / "logs"
    PIDS_DIR = PLATFORM_DIR / "pids"
    CONFIG_DIR = PLATFORM_DIR / "config"
    
    # Device management directories
    DEVICE_CONFIG_DIRS = {
        "config-backups": Path("/home/keith/config-backups"),
        "config-backups-auto": Path("/home/keith/config-backups-auto"),
        "config-snapshots": Path("/home/keith/config-snapshots"),
        "fortigate-configs": Path("/home/keith/fortigate-configs"),
        "network-device-configs": Path("/home/keith/network-device-configs")
    }
    
    # Cleanup configurations
    CLEANUP_CONFIGS = {
        "config-backups": CleanupConfig(
            directory=DEVICE_CONFIG_DIRS["config-backups"],
            retention_days=90,
            file_patterns=["*.conf", "*.cfg", "*.backup", "*.json"],
            size_limit_mb=500
        ),
        "config-backups-auto": CleanupConfig(
            directory=DEVICE_CONFIG_DIRS["config-backups-auto"],
            retention_days=30,
            file_patterns=["*.conf", "*.cfg", "*.backup"],
            size_limit_mb=200
        ),
        "config-snapshots": CleanupConfig(
            directory=DEVICE_CONFIG_DIRS["config-snapshots"],
            retention_days=60,
            file_patterns=["*.snapshot", "*.json", "*.xml"],
            size_limit_mb=300
        ),
        "platform-logs": CleanupConfig(
            directory=LOGS_DIR,
            retention_days=14,
            file_patterns=["*.log", "*.out"],
            size_limit_mb=100
        )
    }
    
    # Power Automate configuration
    POWER_AUTOMATE = PowerAutomateConfig(
        webhook_url=os.getenv("POWER_AUTOMATE_WEBHOOK_URL", ""),
        enabled=bool(os.getenv("POWER_AUTOMATE_ENABLED", "true").lower() == "true"),
        events=[
            PowerAutomateEventType.PLATFORM_STARTUP,
            PowerAutomateEventType.SERVICE_HEALTH,
            PowerAutomateEventType.CONFIG_CLEANUP,
            PowerAutomateEventType.ERROR_ALERT
        ]
    )
    
    # Tailscale configuration
    TAILSCALE_DOMAIN = "ubuntuaicodeserver-1.tail5137b4.ts.net"
    TAILSCALE_NET = "tail5137b4"
    
    # Service definitions with Power Automate monitoring
    SERVICES = {
        # Core AI Services
        "chat-copilot-backend": ServiceConfig(
            name="chat-copilot-backend",
            port=11000,
            command="cd {platform_dir}/webapi && dotnet run --urls http://0.0.0.0:11000",
            health_path="/healthz",
            service_type=ServiceType.CORE,
            power_automate_monitor=True
        ),
        "autogen-studio": ServiceConfig(
            name="autogen-studio",
            port=11001,
            command="autogenstudio ui --port 11001 --host 0.0.0.0",
            health_path="/",
            service_type=ServiceType.CORE,
            use_uv=True,
            power_automate_monitor=True
        ),
        "webhook-server": ServiceConfig(
            name="webhook-server",
            port=11002,
            command="node {platform_dir}/webhook-server.js",
            health_path="/health",
            service_type=ServiceType.CORE
        ),
        "magentic-one": ServiceConfig(
            name="magentic-one",
            port=11003,
            command="python {platform_dir}/magentic_one_server.py",
            health_path="/health",
            service_type=ServiceType.CORE,
            use_uv=True
        ),
        
        # Device Management Services
        "fortimanager-app": ServiceConfig(
            name="fortimanager-app",
            port=11050,
            command="cd /home/keith/fortimanager-real-time-web-app && python app.py",
            health_path="/health",
            service_type=ServiceType.DEVICE_MANAGEMENT,
            use_uv=True,
            power_automate_monitor=True
        ),
        "fortigate-dashboard": ServiceConfig(
            name="fortigate-dashboard",
            port=11051,
            command="cd /home/keith/fortigate-dashboard && python app.py",
            health_path="/",
            service_type=ServiceType.DEVICE_MANAGEMENT,
            use_uv=True,
            power_automate_monitor=True
        ),
        "network-device-mapper": ServiceConfig(
            name="network-device-mapper",
            port=11052,
            command="cd /home/keith/Network-Device-Mapper && python app.py",
            health_path="/api/health",
            service_type=ServiceType.DEVICE_MANAGEMENT,
            use_uv=True,
            power_automate_monitor=True
        ),
        
        # Infrastructure Services
        "port-scanner": ServiceConfig(
            name="port-scanner",
            port=11010,
            command="cd /home/keith/port-scanner-material-ui && node backend/server.js",
            health_path="/nmap-status",
            service_type=ServiceType.INFRASTRUCTURE
        ),
        
        # Docker Services
        "nginx-proxy": ServiceConfig(
            name="nginx-proxy",
            port=11080,
            compose_file="{platform_dir}/docker-compose.nginx-proxy-manager.yml",
            health_path="/",
            service_type=ServiceType.DOCKER
        ),
        "fortinet-manager": ServiceConfig(
            name="fortinet-manager",
            port=3001,
            compose_file="/home/keith/fortinet-manager/docker-compose.yml",
            health_path="/",
            service_type=ServiceType.DOCKER,
            power_automate_monitor=True
        ),
        
        # External Services
        "ollama": ServiceConfig(
            name="ollama",
            port=11434,
            host="localhost",
            health_path="/api/version",
            service_type=ServiceType.EXTERNAL
        ),
        "perplexica": ServiceConfig(
            name="perplexica",
            port=11020,
            health_path="/",
            service_type=ServiceType.EXTERNAL
        ),
        "openwebui": ServiceConfig(
            name="openwebui",
            port=11880,
            health_path="/api/config",
            service_type=ServiceType.EXTERNAL
        ),
    }


class PlatformLogger:
    """Enhanced logging with Power Automate integration"""
    
    def __init__(self, name: str = "platform"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Create file handler
        log_file = PlatformConfig.LOGS_DIR / f"{name}.log"
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Create console handler with colors
        console_handler = logging.StreamHandler()
        console_formatter = ColoredFormatter()
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
    
    def info(self, message: str, emoji: str = "✅"):
        self.logger.info(f"{emoji} {message}")
    
    def warn(self, message: str, emoji: str = "⚠️"):
        self.logger.warning(f"{emoji} {message}")
    
    def error(self, message: str, emoji: str = "❌"):
        self.logger.error(f"{emoji} {message}")
    
    def debug(self, message: str, emoji: str = "🔍"):
        self.logger.debug(f"{emoji} {message}")
    
    def title(self, message: str, emoji: str = "🚀"):
        self.logger.info(f"\n{emoji} {message}")


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {record.levelname}: {record.getMessage()}"


class PowerAutomateIntegration:
    """Power Automate webhook integration for platform monitoring"""
    
    def __init__(self, config: PowerAutomateConfig, logger: PlatformLogger):
        self.config = config
        self.logger = logger
        self.session = None
    
    async def __aenter__(self):
        if self.config.enabled and self.config.webhook_url:
            try:
                import aiohttp
                self.session = aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                )
            except ImportError:
                self.logger.warn("aiohttp not available - Power Automate integration disabled")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def send_event(self, event_type: PowerAutomateEventType, data: Dict[str, Any]) -> bool:
        """Send event to Power Automate webhook"""
        if not self.config.enabled or not self.config.webhook_url or event_type not in self.config.events:
            return False
        
        if not self.session:
            self.logger.warn("Power Automate session not initialized")
            return False
        
        payload = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type.value,
            "platform": "AI Research Platform",
            "source": "platform_manager",
            "data": data
        }
        
        for attempt in range(1, self.config.retry_attempts + 1):
            try:
                async with self.session.post(self.config.webhook_url, json=payload) as response:
                    if response.status == 200:
                        self.logger.debug(f"Power Automate event sent: {event_type.value}")
                        return True
                    else:
                        self.logger.warn(f"Power Automate responded with status {response.status}")
            except Exception as e:
                self.logger.warn(f"Power Automate attempt {attempt} failed: {e}")
                if attempt < self.config.retry_attempts:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        self.logger.error(f"Failed to send Power Automate event after {self.config.retry_attempts} attempts")
        return False
    
    async def send_platform_startup(self, service_status: Dict[str, bool]):
        """Send platform startup event"""
        healthy_services = sum(1 for status in service_status.values() if status)
        total_services = len(service_status)
        
        data = {
            "total_services": total_services,
            "healthy_services": healthy_services,
            "health_percentage": (healthy_services / total_services * 100) if total_services > 0 else 0,
            "unhealthy_services": [name for name, status in service_status.items() if not status],
            "services": service_status
        }
        
        await self.send_event(PowerAutomateEventType.PLATFORM_STARTUP, data)
    
    async def send_service_health_alert(self, service_name: str, is_healthy: bool, details: Dict[str, Any]):
        """Send service health alert"""
        data = {
            "service_name": service_name,
            "is_healthy": is_healthy,
            "status": "healthy" if is_healthy else "unhealthy",
            "details": details
        }
        
        await self.send_event(PowerAutomateEventType.SERVICE_HEALTH, data)
    
    async def send_cleanup_report(self, cleanup_results: Dict[str, Any]):
        """Send cleanup operation results"""
        data = {
            "cleanup_results": cleanup_results,
            "total_files_processed": sum(r.get("files_processed", 0) for r in cleanup_results.values()),
            "total_space_freed_mb": sum(r.get("space_freed_mb", 0) for r in cleanup_results.values())
        }
        
        await self.send_event(PowerAutomateEventType.CONFIG_CLEANUP, data)
    
    async def send_error_alert(self, error_type: str, message: str, details: Dict[str, Any]):
        """Send error alert"""
        data = {
            "error_type": error_type,
            "message": message,
            "details": details
        }
        
        await self.send_event(PowerAutomateEventType.ERROR_ALERT, data)


class DirectoryCleanupManager:
    """Manager for cleaning up config backup directories"""
    
    def __init__(self, logger: PlatformLogger):
        self.logger = logger
    
    async def cleanup_all_directories(self, cleanup_configs: Dict[str, CleanupConfig]) -> Dict[str, Any]:
        """Clean up all configured directories"""
        self.logger.title("Starting Directory Cleanup Operations")
        
        cleanup_results = {}
        total_files_processed = 0
        total_space_freed = 0
        
        for name, config in cleanup_configs.items():
            if not config.enabled:
                self.logger.info(f"Skipping disabled cleanup: {name}")
                continue
            
            try:
                result = await self.cleanup_directory(name, config)
                cleanup_results[name] = result
                total_files_processed += result["files_processed"]
                total_space_freed += result["space_freed_mb"]
                
            except Exception as e:
                self.logger.error(f"Cleanup failed for {name}: {e}")
                cleanup_results[name] = {
                    "success": False,
                    "error": str(e),
                    "files_processed": 0,
                    "space_freed_mb": 0
                }
        
        # Summary
        self.logger.info(f"Cleanup complete: {total_files_processed} files, {total_space_freed:.2f} MB freed")
        
        return {
            "total_files_processed": total_files_processed,
            "total_space_freed_mb": total_space_freed,
            "directory_results": cleanup_results
        }
    
    async def cleanup_directory(self, name: str, config: CleanupConfig) -> Dict[str, Any]:
        """Clean up a specific directory based on configuration"""
        if not config.directory.exists():
            self.logger.warn(f"Directory does not exist: {config.directory}")
            return {"success": False, "error": "Directory not found", "files_processed": 0, "space_freed_mb": 0}
        
        self.logger.info(f"Cleaning up {name}: {config.directory}")
        
        cutoff_date = datetime.now() - timedelta(days=config.retention_days)
        files_processed = 0
        space_freed = 0
        errors = []
        
        try:
            # Get all files matching patterns
            all_files = []
            for pattern in config.file_patterns:
                all_files.extend(config.directory.rglob(pattern))
            
            # Sort by modification time (oldest first)
            all_files.sort(key=lambda f: f.stat().st_mtime)
            
            # Calculate current directory size
            current_size_mb = sum(f.stat().st_size for f in all_files if f.is_file()) / (1024 * 1024)
            
            for file_path in all_files:
                try:
                    if not file_path.is_file():
                        continue
                    
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    file_size_mb = file_path.stat().st_size / (1024 * 1024)
                    should_delete = False
                    reason = ""
                    
                    # Check age-based deletion
                    if file_mtime < cutoff_date:
                        should_delete = True
                        reason = f"older than {config.retention_days} days"
                    
                    # Check size-based deletion (if directory exceeds limit)
                    elif config.size_limit_mb and current_size_mb > config.size_limit_mb:
                        should_delete = True
                        reason = f"directory exceeds {config.size_limit_mb} MB limit"
                    
                    if should_delete:
                        self.logger.debug(f"Deleting {file_path.name}: {reason}")
                        file_path.unlink()
                        files_processed += 1
                        space_freed += file_size_mb
                        current_size_mb -= file_size_mb
                        
                        # Stop if we're under the size limit
                        if config.size_limit_mb and current_size_mb <= config.size_limit_mb:
                            break
                
                except Exception as e:
                    errors.append(f"Error deleting {file_path}: {e}")
                    self.logger.debug(f"Error deleting {file_path}: {e}")
            
            # Clean up empty directories
            await self._remove_empty_directories(config.directory)
            
            self.logger.info(f"Cleaned {name}: {files_processed} files, {space_freed:.2f} MB freed")
            
            return {
                "success": True,
                "files_processed": files_processed,
                "space_freed_mb": round(space_freed, 2),
                "directory_size_mb": round(current_size_mb, 2),
                "errors": errors
            }
        
        except Exception as e:
            self.logger.error(f"Cleanup failed for {name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "files_processed": files_processed,
                "space_freed_mb": round(space_freed, 2)
            }
    
    async def _remove_empty_directories(self, directory: Path):
        """Remove empty subdirectories"""
        for dirpath in sorted(directory.rglob("*"), key=lambda p: len(p.parts), reverse=True):
            if dirpath.is_dir() and dirpath != directory:
                try:
                    if not any(dirpath.iterdir()):
                        dirpath.rmdir()
                        self.logger.debug(f"Removed empty directory: {dirpath}")
                except OSError:
                    pass  # Directory not empty or other error


class ServiceManager:
    """Enhanced service manager with Power Automate integration"""
    
    def __init__(self, config: ServiceConfig, platform_config: PlatformConfig, logger: PlatformLogger, power_automate: PowerAutomateIntegration):
        self.config = config
        self.platform_config = platform_config
        self.logger = logger
        self.power_automate = power_automate
        self.process: Optional[subprocess.Popen] = None
        self.pid_file = platform_config.PIDS_DIR / f"{config.name}.pid"
        self.log_file = platform_config.LOGS_DIR / f"{config.name}.log"
        self._port_check_cache: Optional[bool] = None  # cache result within single start attempt
    
    # ------------------------------------------------------------------
    # Helper utilities
    # ------------------------------------------------------------------
    def _is_port_in_use(self) -> bool:
        """Return True if something is already listening on self.config.port"""
        if self._port_check_cache is not None:
            return self._port_check_cache

        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex(("127.0.0.1", self.config.port))
            in_use = result == 0

        # Fallback to ss if socket approach fails to detect (covers IPv6 / 0.0.0.0 bindings)
        if not in_use:
            try:
                out = subprocess.check_output(["ss", "-ltn"], text=True)
                if any(f":{self.config.port} " in line or f":{self.config.port}\n" in line for line in out.splitlines()):
                    in_use = True
            except Exception:
                pass

        self._port_check_cache = in_use
        return in_use

    def _is_docker_port_published(self) -> bool:
        """Return True if any running container is publishing the target host port"""
        try:
            out = subprocess.check_output(["docker", "ps", "--format", "{{.Ports}}"], text=True)
            for line in out.splitlines():
                # line examples: '0.0.0.0:2019->2019/tcp', ':::2019->2019/tcp'
                if f":{self.config.port}->" in line:
                    return True
        except Exception:
            pass
        return False

    async def start(self) -> bool:
        """Start the service with Power Automate monitoring"""
        try:
            await self._stop_existing()
            
            if self.config.service_type == ServiceType.DOCKER:
                success = await self._start_docker_service()
            elif self.config.service_type == ServiceType.EXTERNAL:
                success = await self._check_external_service()
            else:
                success = await self._start_process_service()
            
            # Send Power Automate notification if monitoring is enabled
            if self.config.power_automate_monitor:
                await self.power_automate.send_service_health_alert(
                    self.config.name,
                    success,
                    {
                        "port": self.config.port,
                        "service_type": self.config.service_type.value,
                        "startup_time": datetime.now().isoformat()
                    }
                )
            
            return success
                
        except Exception as e:
            self.logger.error(f"Failed to start {self.config.name}: {e}")
            
            # Send error alert to Power Automate
            if self.config.power_automate_monitor:
                await self.power_automate.send_error_alert(
                    "service_startup_failed",
                    f"Failed to start {self.config.name}",
                    {"service": self.config.name, "error": str(e)}
                )
            
            return False
    
    async def _start_process_service(self) -> bool:
        """Start a regular process service"""
        if not self.config.command:
            self.logger.error(f"No command specified for {self.config.name}")
            return False
        
        # If port already in use and healthy, skip starting
        if self._is_port_in_use():
            if await self._wait_for_health():
                self.logger.info(f"{self.config.name} already running on port {self.config.port}; skipping start")
                return True
            else:
                self.logger.warn(f"Port {self.config.port} is busy but {self.config.name} health check failed; not attempting restart to avoid conflict")
                return False
        
        # Format command with platform directory
        command = self.config.command.format(platform_dir=self.platform_config.PLATFORM_DIR)
        
        # Setup UV environment if needed
        if self.config.use_uv:
            uv_activate = f"cd {self.platform_config.PLATFORM_DIR} && source .venv/bin/activate && "
            command = uv_activate + command
        
        self.logger.debug(f"Starting {self.config.name} with command: {command}")
        
        # Start process
        with open(self.log_file, 'w') as log:
            self.process = subprocess.Popen(
                command,
                shell=True,
                stdout=log,
                stderr=log,
                preexec_fn=os.setsid
            )
        
        # Save PID
        with open(self.pid_file, 'w') as f:
            f.write(str(self.process.pid))
        
        self.logger.info(f"Started {self.config.name} (PID: {self.process.pid}, Port: {self.config.port})")
        
        # Health check
        if await self._wait_for_health():
            self.logger.info(f"{self.config.name} is healthy")
            return True
        else:
            self.logger.warn(f"{self.config.name} may not be responding properly")
            return False
    
    async def _start_docker_service(self) -> bool:
        """Start a Docker Compose service"""
        if not self.config.compose_file:
            self.logger.error(f"No compose file specified for {self.config.name}")
            return False
        
        # Skip if port already bound by any process or container
        if self._is_port_in_use() or self._is_docker_port_published():
            self.logger.info(f"{self.config.name} port {self.config.port} already in use; assuming service is running and skipping docker-compose up")
            return True
        
        compose_file = self.config.compose_file.format(platform_dir=self.platform_config.PLATFORM_DIR)
        
        if not Path(compose_file).exists():
            self.logger.error(f"Docker compose file not found: {compose_file}")
            return False
        
        # Start the service
        result = subprocess.run(
            f"docker-compose -f {compose_file} up -d",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            self.logger.info(f"{self.config.name} Docker stack started")
            return await self._wait_for_health()
        else:
            # If failure relates to port allocation, assume stack already running elsewhere
            if "port is already allocated" in result.stderr.lower() or self._is_port_in_use():
                self.logger.info(f"{self.config.name} appears to be already running (port {self.config.port} bound). Skipping.")
                return True
            self.logger.error(f"Failed to start {self.config.name}: {result.stderr.strip()}")
            return False
    
    async def _check_external_service(self) -> bool:
        """Check if external service is running"""
        if await self._wait_for_health():
            self.logger.info(f"{self.config.name} is running (Port: {self.config.port})")
            return True
        else:
            self.logger.warn(f"{self.config.name} not responding")
            return False
    
    async def _wait_for_health(self) -> bool:
        """Wait for service to become healthy"""
        url = f"http://{self.config.host}:{self.config.port}{self.config.health_path}"
        
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                for attempt in range(1, self.config.timeout + 1):
                    try:
                        async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                            if response.status < 400:
                                return True
                    except Exception:
                        pass
                    
                    if attempt < self.config.timeout:
                        await asyncio.sleep(2)
        except ImportError:
            # Fallback to subprocess curl if aiohttp not available
            for attempt in range(1, self.config.timeout + 1):
                try:
                    result = subprocess.run(
                        ["curl", "-s", "--max-time", "5", url],
                        capture_output=True,
                        timeout=10
                    )
                    if result.returncode == 0:
                        return True
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    pass
                
                if attempt < self.config.timeout:
                    await asyncio.sleep(2)
        
        return False
    
    async def _stop_existing(self):
        """Stop existing process if running"""
        if self.pid_file.exists():
            try:
                with open(self.pid_file, 'r') as f:
                    old_pid = int(f.read().strip())
                
                # Try to use psutil for better process management
                try:
                    import psutil
                    if psutil.pid_exists(old_pid):
                        self.logger.debug(f"Stopping existing {self.config.name} process (PID: {old_pid})")
                        process = psutil.Process(old_pid)
                        process.terminate()
                        try:
                            process.wait(timeout=5)
                        except psutil.TimeoutExpired:
                            process.kill()
                except ImportError:
                    # Fallback to basic kill if psutil not available
                    try:
                        os.kill(old_pid, 15)  # SIGTERM
                        await asyncio.sleep(2)
                        try:
                            os.kill(old_pid, 9)  # SIGKILL (if still running)
                        except (OSError, ProcessLookupError):
                            pass
                    except (OSError, ProcessLookupError):
                        pass
                except Exception:
                    # Fallback if psutil fails
                    try:
                        os.kill(old_pid, 15)
                        await asyncio.sleep(2)
                        try:
                            os.kill(old_pid, 9)
                        except (OSError, ProcessLookupError):
                            pass
                    except (OSError, ProcessLookupError):
                        pass
                
                self.pid_file.unlink()
            except (ValueError, FileNotFoundError):
                pass


class PlatformManager:
    """Enhanced platform manager with Power Automate and cleanup capabilities"""
    
    def __init__(self):
        self.config = PlatformConfig()
        self.logger = PlatformLogger()
        self.cleanup_manager = DirectoryCleanupManager(self.logger)
        self.services: Dict[str, ServiceManager] = {}
        self.service_status: Dict[str, bool] = {}
        self.power_automate: Optional[PowerAutomateIntegration] = None
    
    async def startup(self):
        """Main startup orchestration with cleanup and Power Automate integration"""
        self.logger.title("AI Research Platform Startup v4.0 with Power Automate")
        self.logger.info(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"Platform Directory: {self.config.PLATFORM_DIR}")
        
        async with PowerAutomateIntegration(self.config.POWER_AUTOMATE, self.logger) as power_automate:
            self.power_automate = power_automate
            
            # Initialize service managers
            for name, service_config in self.config.SERVICES.items():
                self.services[name] = ServiceManager(service_config, self.config, self.logger, power_automate)
            
            try:
                # Phase 1: Prerequisites and cleanup
                await self._setup_prerequisites()
                cleanup_results = await self.cleanup_manager.cleanup_all_directories(self.config.CLEANUP_CONFIGS)
                await power_automate.send_cleanup_report(cleanup_results.get("directory_results", {}))
                
                # Phase 2: Service startup
                await self._start_services_by_type()
                
                # Phase 3: Health verification
                self.logger.title("Service Health Verification")
                await asyncio.sleep(5)
                await self._verify_all_services()
                
                # Phase 4: Status reporting and Power Automate notification
                await self._generate_status_report()
                await power_automate.send_platform_startup(self.service_status)
                self._display_access_information()
                
                self.logger.info("✅ AI Research Platform startup complete!")
                
            except Exception as e:
                self.logger.error(f"Platform startup failed: {e}")
                await power_automate.send_error_alert(
                    "platform_startup_failed",
                    f"Platform startup failed: {e}",
                    {"timestamp": datetime.now().isoformat()}
                )
                raise
    
    async def _setup_prerequisites(self):
        """Setup directories and check dependencies"""
        self.logger.title("Setting Up Prerequisites")
        
        # Create all necessary directories
        all_dirs = [
            self.config.LOGS_DIR,
            self.config.PIDS_DIR,
            self.config.CONFIG_DIR
        ] + list(self.config.DEVICE_CONFIG_DIRS.values())
        
        for directory in all_dirs:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Check network connectivity
        await self._wait_for_network()
        
        # Setup UV environment
        await self._setup_uv_environment()
    
    async def _wait_for_network(self):
        """Wait for network connectivity"""
        self.logger.info("Checking network connectivity...")
        
        for _ in range(30):
            try:
                result = subprocess.run(
                    ["ping", "-c", "1", "8.8.8.8"],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    self.logger.info("Network connectivity confirmed")
                    return
            except subprocess.TimeoutExpired:
                pass
            
            await asyncio.sleep(2)
            
            await asyncio.sleep(2)
        
        raise Exception("Network timeout - no connectivity")
    
    async def _setup_uv_environment(self):
        """Setup UV Python environment"""
        self.logger.info("Setting up UV environment...")
        
        # Install UV if not present
        if not Path.home().joinpath(".cargo/bin/uv").exists():
            self.logger.info("Installing UV...")
            subprocess.run(
                "curl -LsSf https://astral.sh/uv/install.sh | sh",
                shell=True,
                check=True
            )
        
        # Create virtual environment if needed
        venv_path = self.config.PLATFORM_DIR / ".venv"
        if not venv_path.exists():
            subprocess.run(
                f"cd {self.config.PLATFORM_DIR} && uv venv --python 3.11",
                shell=True,
                check=True
            )
            self.logger.info("Created UV virtual environment")
    
    async def _start_services_by_type(self):
        """Start services in order by type"""
        service_types = [
            ServiceType.EXTERNAL,         # Check external first
            ServiceType.CORE,             # Core AI services
            ServiceType.DEVICE_MANAGEMENT, # Device management services
            ServiceType.INFRASTRUCTURE,   # Infrastructure
            ServiceType.DOCKER,           # Docker services last
        ]
        
        for service_type in service_types:
            self.logger.title(f"Starting {service_type.value.title().replace('_', ' ')} Services")
            
            # Get services of this type
            services_to_start = [
                (name, service) for name, service in self.services.items()
                if self.config.SERVICES[name].service_type == service_type
            ]
            
            if not services_to_start:
                continue
            
            # Start services concurrently within each type
            tasks = []
            for name, service in services_to_start:
                tasks.append(self._start_service_with_status(name, service))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Log any exceptions
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    service_name = services_to_start[i][0]
                    self.logger.error(f"Failed to start {service_name}: {result}")
    
    async def _start_service_with_status(self, name: str, service: ServiceManager) -> bool:
        """Start a service and track its status"""
        try:
            success = await service.start()
            self.service_status[name] = success
            return success
        except Exception as e:
            self.logger.error(f"Exception starting {name}: {e}")
            self.service_status[name] = False
            return False
    
    async def _verify_all_services(self):
        """Verify health of all services"""
        for name, _ in self.services.items():
            config = self.config.SERVICES[name]
            if config.service_type == ServiceType.EXTERNAL:
                url = f"http://{config.host}:{config.port}{config.health_path}"
                try:
                    import aiohttp
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                            if response.status < 400:
                                self.logger.info(f"{name} is healthy")
                                self.service_status[name] = True
                            else:
                                self.logger.warn(f"{name} responded with status {response.status}")
                                self.service_status[name] = False
                except ImportError:
                    # Fallback to curl if aiohttp not available
                    try:
                        result = subprocess.run(
                            ["curl", "-s", "--max-time", "5", url],
                            capture_output=True,
                            timeout=10
                        )
                        if result.returncode == 0:
                            self.logger.info(f"{name} is healthy")
                            self.service_status[name] = True
                        else:
                            self.logger.warn(f"{name} not responding")
                            self.service_status[name] = False
                    except (subprocess.TimeoutExpired, FileNotFoundError):
                        self.logger.warn(f"{name} health check failed")
                        self.service_status[name] = False
                except Exception:
                    self.logger.warn(f"{name} not responding")
                    self.service_status[name] = False
    
    async def _generate_status_report(self):
        """Generate comprehensive status report"""
        self.logger.title("Generating Status Report")
        
        status_report = {
            "platform": {
                "name": "AI Research Platform",
                "version": "4.0",
                "startup_time": time.strftime('%Y-%m-%dT%H:%M:%S'),
                "port_range": "11000-12000",
                "power_automate_enabled": self.config.POWER_AUTOMATE.enabled
            },
            "cleanup": {
                "enabled_directories": [name for name, config in self.config.CLEANUP_CONFIGS.items() if config.enabled],
                "last_cleanup": datetime.now().isoformat()
            },
            "services": {}
        }
        
        # Group services by type
        for service_type in ServiceType:
            type_services = {}
            for name, config in self.config.SERVICES.items():
                if config.service_type == service_type:
                    type_services[name] = {
                        "port": config.port,
                        "status": "running" if self.service_status.get(name, False) else "stopped",
                        "local_url": f"http://{config.host}:{config.port}",
                        "tailscale_url": f"https://{name}.{self.config.TAILSCALE_DOMAIN}/",
                        "power_automate_monitor": config.power_automate_monitor
                    }
            
            if type_services:
                status_report["services"][service_type.value] = type_services
        
        # Save status report
        status_file = self.config.PLATFORM_DIR / "platform-status.json"
        with open(status_file, 'w') as f:
            json.dump(status_report, f, indent=2)
        
        self.logger.info(f"Status report saved: {status_file}")
    
    def _display_access_information(self):
        """Display platform access information"""
        self.logger.title("Platform Access Information")
        
        print("\n🤖 AI SERVICES:")
        for name, config in self.config.SERVICES.items():
            if config.service_type == ServiceType.CORE:
                status = "✅" if self.service_status.get(name, False) else "❌"
                monitor = "📊" if config.power_automate_monitor else ""
                print(f"   {status} {monitor} {name.title()}: http://{config.host}:{config.port}")
        
        print("\n🛠️ DEVICE MANAGEMENT:")
        for name, config in self.config.SERVICES.items():
            if config.service_type == ServiceType.DEVICE_MANAGEMENT:
                status = "✅" if self.service_status.get(name, False) else "❌"
                monitor = "📊" if config.power_automate_monitor else ""
                print(f"   {status} {monitor} {name.title()}: http://{config.host}:{config.port}")
        
        print("\n🔧 INFRASTRUCTURE:")
        for name, config in self.config.SERVICES.items():
            if config.service_type in [ServiceType.INFRASTRUCTURE, ServiceType.DOCKER]:
                status = "✅" if self.service_status.get(name, False) else "❌"
                print(f"   {status} {name.title()}: http://{config.host}:{config.port}")
        
        if self.config.POWER_AUTOMATE.enabled:
            print(f"\n📊 POWER AUTOMATE:")
            print(f"   ✅ Webhook Integration: Enabled")
            print(f"   📨 Monitored Events: {len(self.config.POWER_AUTOMATE.events)}")
            monitored_services = [name for name, config in self.config.SERVICES.items() if config.power_automate_monitor]
            print(f"   🔍 Monitored Services: {len(monitored_services)}")
        
        print(f"\n🧹 CLEANUP STATUS:")
        enabled_cleanups = [name for name, config in self.config.CLEANUP_CONFIGS.items() if config.enabled]
        print(f"   ✅ Enabled Directories: {len(enabled_cleanups)}")
        print(f"   📁 Directories: {', '.join(enabled_cleanups)}")


async def main():
    """Main entry point"""
    try:
        platform = PlatformManager()
        await platform.startup()
    except KeyboardInterrupt:
        print("\n🛑 Startup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    
    # Install required packages if needed
    try:
        import aiohttp  # Test if aiohttp is available
        del aiohttp  # Clean up to avoid unused warning
    except ImportError:
        print("📦 Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp", "psutil"])
    
    asyncio.run(main())
