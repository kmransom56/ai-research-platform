"""
SSL Universal Fix for Corporate Networks (Zscaler, Proxy, etc.)
Handles SSL certificate issues common in corporate environments
"""

import ssl
import urllib3
import certifi
import os
import requests
from urllib3.exceptions import InsecureRequestWarning
import logging

logger = logging.getLogger(__name__)

def apply_all_ssl_fixes(verbose=True):
    """
    Apply comprehensive SSL fixes for corporate environments
    
    Args:
        verbose (bool): Enable detailed logging of SSL fixes applied
    """
    
    fixes_applied = []
    
    try:
        # 1. Disable urllib3 SSL warnings
        urllib3.disable_warnings(InsecureRequestWarning)
        fixes_applied.append("urllib3 SSL warnings disabled")
        
        # 2. Create unverified SSL context
        ssl._create_default_https_context = ssl._create_unverified_context
        fixes_applied.append("Default SSL context set to unverified")
        
        # 3. Set environment variables for SSL bypass
        os.environ['PYTHONHTTPSVERIFY'] = '0'
        os.environ['CURL_CA_BUNDLE'] = ''
        os.environ['REQUESTS_CA_BUNDLE'] = ''
        fixes_applied.append("Environment variables set for SSL bypass")
        
        # 4. Configure requests to ignore SSL
        requests.packages.urllib3.disable_warnings()
        fixes_applied.append("Requests SSL warnings disabled")
        
        # 5. Monkey patch requests Session for corporate proxies
        original_request = requests.Session.request
        
        def patched_request(self, method, url, **kwargs):
            # Always disable SSL verification for corporate networks
            kwargs.setdefault('verify', False)
            return original_request(self, method, url, **kwargs)
        
        requests.Session.request = patched_request
        fixes_applied.append("Requests Session patched for SSL bypass")
        
        if verbose:
            print(f"[SSL Universal Fix] Applied {len(fixes_applied)} fixes:")
            for fix in fixes_applied:
                print(f"  ✅ {fix}")
        
        return True
        
    except Exception as e:
        if verbose:
            print(f"[SSL Universal Fix] Error applying fixes: {str(e)}")
        logger.error(f"SSL fix error: {str(e)}")
        return False

def configure_zscaler_environment():
    """
    Configure environment for Zscaler corporate proxy
    """
    
    # Common Zscaler proxy configurations
    zscaler_configs = {
        # Disable certificate verification
        'PYTHONHTTPSVERIFY': '0',
        'SSL_VERIFY': 'false', 
        'REQUESTS_CA_BUNDLE': '',
        'CURL_CA_BUNDLE': '',
        
        # Common corporate proxy settings
        'NO_PROXY': 'localhost,127.0.0.1,*.local',
        
        # Trust corporate certificates if available
        'CORPORATE_CERT_PATH': '/etc/ssl/certs/corporate-ca.crt'
    }
    
    applied = []
    for key, value in zscaler_configs.items():
        if key not in os.environ:
            os.environ[key] = value
            applied.append(f"{key}={value}")
    
    return applied

def create_ssl_context_for_corporate():
    """
    Create SSL context suitable for corporate environments
    """
    
    # Create context that accepts self-signed certificates
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    
    # Allow all ciphers (some corporate proxies use weak ciphers)
    context.set_ciphers('ALL:@SECLEVEL=0')
    
    return context

def patch_requests_for_fortimanager():
    """
    Specific patches for FortiManager API calls through corporate proxies
    """
    
    import requests.adapters
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    
    class CorporateHTTPAdapter(HTTPAdapter):
        def init_poolmanager(self, *args, **kwargs):
            kwargs['ssl_context'] = create_ssl_context_for_corporate()
            return super().init_poolmanager(*args, **kwargs)
    
    # Monkey patch for all requests
    original_session = requests.Session
    
    class CorporateSession(original_session):
        def __init__(self):
            super().__init__()
            # Mount the custom adapter
            self.mount('https://', CorporateHTTPAdapter())
            self.verify = False
            
            # Set aggressive timeouts for corporate networks
            self.timeout = (30, 60)  # (connect, read)
            
            # Add retry strategy
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504]
            )
            
            adapter = HTTPAdapter(max_retries=retry_strategy)
            self.mount('http://', adapter)
            self.mount('https://', CorporateHTTPAdapter())
    
    # Replace default Session
    requests.Session = CorporateSession
    
    return "FortiManager-specific SSL patches applied"

def test_ssl_connectivity(host, port=443):
    """
    Test SSL connectivity to a host (like FortiManager)
    
    Args:
        host (str): Hostname or IP to test
        port (int): Port to test (default 443)
    
    Returns:
        dict: Test results
    """
    
    results = {
        'host': host,
        'port': port,
        'tests': {}
    }
    
    # Test 1: Basic socket connection
    try:
        import socket
        sock = socket.create_connection((host, port), timeout=10)
        sock.close()
        results['tests']['socket'] = '✅ Basic connection successful'
    except Exception as e:
        results['tests']['socket'] = f'❌ Basic connection failed: {str(e)}'
    
    # Test 2: SSL connection with verification
    try:
        context = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                results['tests']['ssl_verified'] = '✅ SSL with verification successful'
    except Exception as e:
        results['tests']['ssl_verified'] = f'❌ SSL with verification failed: {str(e)}'
    
    # Test 3: SSL connection without verification
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        with socket.create_connection((host, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                results['tests']['ssl_unverified'] = '✅ SSL without verification successful'
    except Exception as e:
        results['tests']['ssl_unverified'] = f'❌ SSL without verification failed: {str(e)}'
    
    # Test 4: HTTP request
    try:
        apply_all_ssl_fixes(verbose=False)
        response = requests.get(f'https://{host}:{port}', timeout=10, verify=False)
        results['tests']['http_request'] = f'✅ HTTP request successful (Status: {response.status_code})'
    except Exception as e:
        results['tests']['http_request'] = f'❌ HTTP request failed: {str(e)}'
    
    return results

def print_ssl_diagnostics():
    """
    Print comprehensive SSL diagnostics for troubleshooting
    """
    
    print("🔒 SSL Diagnostics for Corporate Networks")
    print("=" * 60)
    
    # Python SSL info
    print(f"Python SSL Version: {ssl.OPENSSL_VERSION}")
    print(f"Default CA Bundle: {certifi.where()}")
    print(f"SSL Verify Environment: {os.getenv('PYTHONHTTPSVERIFY', 'Not Set')}")
    
    # Environment variables
    ssl_vars = ['PYTHONHTTPSVERIFY', 'REQUESTS_CA_BUNDLE', 'CURL_CA_BUNDLE', 'SSL_VERIFY']
    print(f"\n🌍 Environment Variables:")
    for var in ssl_vars:
        value = os.getenv(var, 'Not Set')
        print(f"  {var}: {value}")
    
    # Certificate paths
    cert_paths = ['/etc/ssl/certs/', '/usr/local/share/ca-certificates/', certifi.where()]
    print(f"\n📜 Certificate Locations:")
    for path in cert_paths:
        if os.path.exists(path):
            print(f"  ✅ {path}")
        else:
            print(f"  ❌ {path}")

def create_fortimanager_session():
    """
    Create a requests session optimized for FortiManager in corporate environments
    
    Returns:
        requests.Session: Configured session
    """
    
    session = requests.Session()
    
    # Apply all SSL fixes
    apply_all_ssl_fixes(verbose=False)
    
    # Configure session for corporate network
    session.verify = False
    session.timeout = (30, 60)
    
    # Headers for FortiManager
    session.headers.update({
        'Content-Type': 'application/json',
        'User-Agent': 'Restaurant-Network-Manager/1.0'
    })
    
    # Custom adapter for SSL
    adapter = requests.adapters.HTTPAdapter(
        max_retries=3,
        pool_connections=10,
        pool_maxsize=10
    )
    
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    return session

if __name__ == "__main__":
    print("🔒 SSL Universal Fix - Corporate Network Helper")
    print("=" * 60)
    
    # Apply all fixes
    apply_all_ssl_fixes(verbose=True)
    
    # Configure Zscaler environment
    zscaler_configs = configure_zscaler_environment()
    if zscaler_configs:
        print(f"\n🏢 Applied Zscaler configurations:")
        for config in zscaler_configs:
            print(f"  ✅ {config}")
    
    # Apply FortiManager patches
    fm_patch = patch_requests_for_fortimanager()
    print(f"\n🛡️  {fm_patch}")
    
    # Print diagnostics
    print()
    print_ssl_diagnostics()
    
    print(f"\n✅ SSL Universal Fix applied - ready for corporate network testing!")