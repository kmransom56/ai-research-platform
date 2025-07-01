#!/usr/bin/env python3
"""
Tailscale HTTPS Automation Script
Automates the process of securing multiple applications with Tailscale certificates
"""

import json
import subprocess
import requests
from pathlib import Path
from typing import Dict, List
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TailscaleHTTPSManager:
    def __init__(self, tailnet_domain: str, machine_ip: str = "100.123.10.72"):
        self.tailnet_domain = tailnet_domain  # e.g., "your-machine.your-tailnet.ts.net"
        self.machine_ip = machine_ip
        self.cert_path = Path("/opt/tailscale-certs")
        self.cert_path.mkdir(exist_ok=True)

        # Application configuration
        self.applications = {
            "copilot": {"port": 11000, "path": "/control-panel.html"},
            "autogen": {"port": 11001, "path": ""},
            "magentic": {"port": 11003, "path": ""},
            "webhook": {"port": 11025, "path": "/health"},
            "portscanner": {"port": 11010, "path": ""},
            "nginx-manager": {"port": 8080, "path": ""},
            "nginx-admin": {"port": 11082, "path": ""},
            "vscode": {"port": 57081, "path": ""},
            "ntopng": {"port": 8888, "path": ""},
            "neo4j": {"port": 7474, "path": ""},
            "genai-stack": {"port": 8505, "path": ""},
            "perplexica": {"port": 11020, "path": "/perplexia"},
            "searxng": {"port": 11021, "path": ""},
            "openwebui": {"port": 8080, "path": ""},
            "ollama": {"port": 11434, "path": "", "internal_only": True},
        }

    def generate_tailscale_certificate(self) -> bool:
        """Generate Tailscale certificate for the domain"""
        try:
            logger.info(f"Generating Tailscale certificate for {self.tailnet_domain}")

            # Run tailscale cert command
            result = subprocess.run(
                ["sudo", "tailscale", "cert", self.tailnet_domain],
                capture_output=True,
                text=True,
                check=True,
            )

            logger.info("Certificate generated successfully")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to generate certificate: {e.stderr}")
            return False

    def get_certificate_paths(self) -> Dict[str, str]:
        """Get paths to certificate files"""
        return {
            "cert": f"{self.tailnet_domain}.crt",
            "key": f"{self.tailnet_domain}.key",
        }

    def create_subdomain_certificates(self) -> bool:
        """Create subdomain certificates for each application"""
        cert_paths = self.get_certificate_paths()

        if not Path(cert_paths["cert"]).exists():
            logger.error("Main certificate not found. Generate it first.")
            return False

        for app_name in self.applications:
            if self.applications[app_name].get("internal_only"):
                continue

            subdomain = f"{app_name}.{self.tailnet_domain}"
            logger.info(f"Creating certificate for {subdomain}")

            try:
                result = subprocess.run(
                    ["sudo", "tailscale", "cert", subdomain],
                    capture_output=True,
                    text=True,
                    check=True,
                )

                logger.info(f"Certificate created for {subdomain}")

            except subprocess.CalledProcessError as e:
                logger.warning(
                    f"Failed to create certificate for {subdomain}: {e.stderr}"
                )
                continue

        return True

    def generate_nginx_configs(self) -> Dict[str, str]:
        """Generate Nginx configuration for each application"""
        configs = {}

        for app_name, config in self.applications.items():
            if config.get("internal_only"):
                continue

            subdomain = f"{app_name}.{self.tailnet_domain}"

            nginx_config = f"""
server {{
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name {subdomain};

    ssl_certificate /etc/ssl/tailscale/{subdomain}.crt;
    ssl_certificate_key /etc/ssl/tailscale/{subdomain}.key;
    
    # SSL Security Headers
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options SAMEORIGIN always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {{
        proxy_pass http://{self.machine_ip}:{config['port']}{config['path']};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }}
}}

# Redirect HTTP to HTTPS
server {{
    listen 80;
    listen [::]:80;
    server_name {subdomain};
    return 301 https://$server_name$request_uri;
}}
"""
            configs[app_name] = nginx_config

        return configs

    def create_docker_compose_override(self) -> str:
        """Create docker-compose override for SSL certificates"""
        return """
version: '3.8'

services:
  nginx-proxy-manager:
    volumes:
      - /opt/tailscale-certs:/etc/ssl/tailscale:ro
      - ./nginx-configs:/etc/nginx/conf.d:ro
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=America/New_York
"""

    def setup_certificate_renewal(self) -> str:
        """Create a script for automatic certificate renewal"""
        renewal_script = f"""#!/bin/bash
# Tailscale Certificate Renewal Script

LOG_FILE="/var/log/tailscale-cert-renewal.log"
NGINX_CONTAINER="nginx-proxy-manager"

log_message() {{
    echo "$(date): $1" >> "$LOG_FILE"
}}

log_message "Starting certificate renewal process"

# Renew main certificate
if sudo tailscale cert {self.tailnet_domain}; then
    log_message "Main certificate renewed successfully"
else
    log_message "Failed to renew main certificate"
    exit 1
fi

# Renew subdomain certificates
"""

        for app_name in self.applications:
            if self.applications[app_name].get("internal_only"):
                continue

            subdomain = f"{app_name}.{self.tailnet_domain}"
            renewal_script += f"""
if sudo tailscale cert {subdomain}; then
    log_message "Certificate for {subdomain} renewed successfully"
else
    log_message "Failed to renew certificate for {subdomain}"
fi
"""

        renewal_script += """
# Restart Nginx to load new certificates
if docker restart "$NGINX_CONTAINER"; then
    log_message "Nginx restarted successfully"
else
    log_message "Failed to restart Nginx"
fi

log_message "Certificate renewal process completed"
"""

        return renewal_script

    def create_monitoring_script(self) -> str:
        """Create a monitoring script to check certificate expiration"""
        return f"""#!/usr/bin/env python3
import ssl
import socket
import datetime
import logging
from typing import List, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_certificate_expiry(hostname: str, port: int = 443) -> Tuple[str, int]:
    \"\"\"Check certificate expiry for a given hostname\"\"\"
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                
        not_after = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
        days_until_expiry = (not_after - datetime.datetime.now()).days
        
        return cert['subject'][0][0][1], days_until_expiry
        
    except Exception as e:
        logger.error(f"Error checking {{hostname}}: {{e}}")
        return hostname, -1

def main():
    applications = {list(self.applications.keys())}
    tailnet_domain = "{self.tailnet_domain}"
    
    logger.info("Checking certificate expiration for all applications...")
    
    for app in applications:
        if app in {[app for app, config in self.applications.items() if config.get("internal_only")]}:
            continue
            
        hostname = f"{{app}}.{{tailnet_domain}}"
        subject, days = check_certificate_expiry(hostname)
        
        if days > 30:
            logger.info(f"{{hostname}}: {{days}} days until expiry ✓")
        elif days > 7:
            logger.warning(f"{{hostname}}: {{days}} days until expiry ⚠️")
        elif days >= 0:
            logger.error(f"{{hostname}}: {{days}} days until expiry ❌")
        else:
            logger.error(f"{{hostname}}: Certificate check failed ❌")

if __name__ == "__main__":
    main()
"""

    def deploy_configuration(self):
        """Deploy the complete HTTPS configuration"""
        logger.info("Starting Tailscale HTTPS deployment...")

        # Step 1: Generate certificates
        if not self.generate_tailscale_certificate():
            return False

        # Step 2: Create subdomain certificates
        if not self.create_subdomain_certificates():
            logger.warning("Some subdomain certificates failed to generate")

        # Step 3: Generate Nginx configurations
        configs = self.generate_nginx_configs()

        # Create nginx-configs directory
        nginx_dir = Path("./nginx-configs")
        nginx_dir.mkdir(exist_ok=True)

        for app_name, config in configs.items():
            config_file = nginx_dir / f"{app_name}.conf"
            config_file.write_text(config)
            logger.info(f"Created Nginx config for {app_name}")

        # Step 4: Create docker-compose override
        Path("./docker-compose.override.yml").write_text(
            self.create_docker_compose_override()
        )

        # Step 5: Create renewal script
        renewal_script = Path("./renew-certificates.sh")
        renewal_script.write_text(self.setup_certificate_renewal())
        renewal_script.chmod(0o755)

        # Step 6: Create monitoring script
        monitoring_script = Path("./check-certificates.py")
        monitoring_script.write_text(self.create_monitoring_script())
        monitoring_script.chmod(0o755)

        logger.info("HTTPS configuration deployed successfully!")
        logger.info("Next steps:")
        logger.info("1. Copy certificates to /opt/tailscale-certs/")
        logger.info("2. Run 'docker-compose up -d' to restart Nginx Proxy Manager")
        logger.info(
            "3. Add renewal script to crontab: '0 2 * * 0 /path/to/renew-certificates.sh'"
        )
        logger.info(
            "4. Add monitoring to crontab: '0 9 * * * /path/to/check-certificates.py'"
        )

        return True


def main():
    import sys

    if len(sys.argv) != 2:
        print("Usage: python3 tailscale_https_setup.py <your-tailnet>.ts.net")
        print("Example: python3 tailscale_https_setup.py tail12345.ts.net")
        print("Find your tailnet name at: https://login.tailscale.com/admin/dns")
        sys.exit(1)

    tailnet_name = sys.argv[1]
    TAILNET_DOMAIN = f"netintegrate.{tailnet_name}"

    print(f"Setting up HTTPS for: {TAILNET_DOMAIN}")
    print(f"Machine IP: 100.123.10.72")
    print()

    manager = TailscaleHTTPSManager(TAILNET_DOMAIN)

    if manager.deploy_configuration():
        print("\n🎉 Setup completed successfully!")
        print(f"\nYour applications will be available at:")
        for app_name in manager.applications:
            if not manager.applications[app_name].get("internal_only"):
                print(f"  • {app_name}: https://{app_name}.{TAILNET_DOMAIN}")
    else:
        print("\n❌ Setup failed. Check the logs above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
