#!/usr/bin/env python3
"""
Certificate Expiration Checker for AI Research Platform
Monitors SSL/TLS certificate expiration dates across Tailscale network
"""

import ssl
import socket
import datetime
import logging
from typing import List, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_certificate_expiry(hostname: str, port: int = 443) -> Tuple[str, int]:
    """
    Check SSL certificate expiration for a given hostname.
    
    Args:
        hostname: The domain name to check
        port: The port number (default: 443 for HTTPS)
    
    Returns:
        Tuple of (certificate_subject, days_until_expiry)
        Returns -1 for days if check fails
    """
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                
        not_after = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
        days_until_expiry = (not_after - datetime.datetime.now()).days
        
        return cert['subject'][0][0][1], days_until_expiry
        
    except Exception as e:
        logger.error(f"Error checking {hostname}: {e}")
        return hostname, -1

def main():
    """
    Main function to check certificate expiration for all AI Research Platform applications.
    Checks certificates for each service subdomain on the Tailscale network.
    """
    applications = ['copilot', 'autogen', 'magentic', 'webhook', 'portscanner', 'nginx-manager', 'http-gateway', 'https-gateway', 'vscode', 'fortinet', 'perplexica', 'searxng', 'openwebui', 'ollama']
    tailnet_domain = "ubuntuaicodeserver-1.tail5137b4.ts.net"
    
    logger.info("Checking certificate expiration for all applications...")
    
    for app in applications:
        if app in ['ollama']:  # Ollama doesn't use HTTPS
            continue
            
        hostname = f"{app}.{tailnet_domain}"
        subject, days = check_certificate_expiry(hostname)
        
        if days > 30:
            logger.info(f"{hostname}: {days} days until expiry ✓")
        elif days > 7:
            logger.warning(f"{hostname}: {days} days until expiry ⚠️")
        elif days >= 0:
            logger.error(f"{hostname}: {days} days until expiry ❌")
        else:
            logger.error(f"{hostname}: Certificate check failed ❌")

if __name__ == "__main__":
    main()
