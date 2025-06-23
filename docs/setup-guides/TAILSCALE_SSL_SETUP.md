# Tailscale SSL Certificate Setup Guide

This guide explains how to set up SSL certificates for the AI Research Platform using Tailscale's built-in certificate generation capabilities.

## Overview

The AI Research Platform uses Tailscale for secure networking and SSL certificate management. Tailscale provides automatic SSL certificates for your tailnet domain and subdomains, which are used by nginx configurations to secure HTTPS access to various services.

## Prerequisites

1. **Tailscale Installed and Authenticated**
   ```bash
   # Install Tailscale (if not already installed)
   curl -fsSL https://tailscale.com/install.sh | sh
   
   # Authenticate with Tailscale
   sudo tailscale up --hostname=ubuntuaicodeserver-1
   ```

2. **MagicDNS and HTTPS Enabled**
   - Go to [Tailscale Admin Console](https://login.tailscale.com/admin/dns)
   - Enable MagicDNS if not already enabled
   - Under 'HTTPS Certificates', click 'Enable HTTPS'

3. **Tailnet Domain Known**
   - Your domain should be: `ubuntuaicodeserver-1.tail5137b4.ts.net`
   - Verify this in your Tailscale admin console

## SSL Certificate Architecture

### Certificate Directories

The system uses multiple certificate directories for different purposes:

1. **Docker SSL Directory**: `/opt/tailscale-certs/`
   - Used for certificate generation and storage
   - Accessible to the user running the platform

2. **Nginx SSL Directory**: `/etc/ssl/tailscale/`
   - Used by nginx configurations
   - Contains copies of certificates for web server use

3. **Tailscale Cert Directory**: `/var/lib/tailscale/certs/`
   - System directory where Tailscale may store certificates
   - Used by some configurations

### Certificate Types

1. **Main Certificate**
   - Domain: `ubuntuaicodeserver-1.tail5137b4.ts.net`
   - Used by the main SSL configuration (`ssl-main.conf`)

2. **Subdomain Certificates**
   - Individual certificates for each application
   - Format: `<app>.ubuntuaicodeserver-1.tail5137b4.ts.net`
   - Applications include: autogen, copilot, fortinet, magentic, webhook, etc.

## Certificate Generation Process

### Automated Setup Script

Use the provided script for complete SSL setup:

```bash
# Navigate to the platform directory
cd /home/keith/chat-copilot

# Run the SSL setup script
./scripts/infrastructure/setup-tailscale-ssl.sh
```

### Manual Certificate Generation

If you need to generate certificates manually:

```bash
# Create certificate directories
sudo mkdir -p /etc/ssl/tailscale
sudo mkdir -p /opt/tailscale-certs
sudo chown $USER:$USER /opt/tailscale-certs

# Navigate to certificate directory
cd /opt/tailscale-certs

# Generate main certificate
tailscale cert ubuntuaicodeserver-1.tail5137b4.ts.net

# Generate subdomain certificates
tailscale cert autogen.ubuntuaicodeserver-1.tail5137b4.ts.net
tailscale cert copilot.ubuntuaicodeserver-1.tail5137b4.ts.net
tailscale cert fortinet.ubuntuaicodeserver-1.tail5137b4.ts.net
# ... repeat for other applications

# Copy certificates to nginx directory
sudo cp *.crt /etc/ssl/tailscale/
sudo cp *.key /etc/ssl/tailscale/
sudo chmod 644 /etc/ssl/tailscale/*.crt
sudo chmod 600 /etc/ssl/tailscale/*.key
```

## Nginx Configuration

### Certificate Path References

The nginx configurations reference certificates using these paths:

```nginx
# Main certificate (ssl-main.conf)
ssl_certificate     /var/lib/tailscale/certs/ubuntuaicodeserver-1.tail5137b4.ts.net.crt;
ssl_certificate_key /var/lib/tailscale/certs/ubuntuaicodeserver-1.tail5137b4.ts.net.key;

# Subdomain certificates (individual .conf files)
ssl_certificate     /etc/ssl/tailscale/autogen.ubuntuaicodeserver-1.tail5137b4.ts.net.crt;
ssl_certificate_key /etc/ssl/tailscale/autogen.ubuntuaicodeserver-1.tail5137b4.ts.net.key;
```

### Configuration Files

Each application has its own nginx configuration file in `/home/keith/chat-copilot/nginx-configs/`:

- `autogen.conf` - AutoGen Studio SSL configuration
- `copilot.conf` - Chat Copilot SSL configuration
- `fortinet.conf` - Fortinet Manager SSL configuration
- `magentic.conf` - Magentic-One SSL configuration
- `ssl-main.conf` - Main SSL configuration with all services
- And more...

## Certificate Renewal

### Automatic Renewal

The platform includes automatic certificate renewal:

1. **Renewal Script**: `/home/keith/chat-copilot/scripts/infrastructure/renew-certificates.sh`
2. **Cron Schedule**: Weekly on Sunday at 2 AM
3. **Process**: Renews all certificates and restarts nginx services

### Manual Renewal

To manually renew certificates:

```bash
# Run the renewal script
./scripts/infrastructure/renew-certificates.sh

# Or force renewal with the setup script
./scripts/infrastructure/setup-tailscale-ssl.sh --renew
```

## Certificate Monitoring

### Check Certificate Status

```bash
# Use the Python monitoring script
python3 /home/keith/chat-copilot/python/utilities/check-certificates.py

# Or verify with the setup script
./scripts/infrastructure/setup-tailscale-ssl.sh --verify
```

### Certificate Expiration

Tailscale certificates typically have a 90-day expiration period. The monitoring system will:

- ✅ **Green**: More than 30 days until expiry
- ⚠️ **Yellow**: 7-30 days until expiry  
- ❌ **Red**: Less than 7 days until expiry

## Troubleshooting

### Common Issues

1. **Certificate Generation Fails**
   ```bash
   # Check Tailscale authentication
   tailscale status
   
   # Re-authenticate if needed
   sudo tailscale up --hostname=ubuntuaicodeserver-1
   ```

2. **Permission Denied Errors**
   ```bash
   # Fix certificate directory permissions
   sudo chown -R $USER:$USER /opt/tailscale-certs
   sudo chmod 755 /etc/ssl/tailscale
   ```

3. **Nginx Cannot Find Certificates**
   ```bash
   # Verify certificate files exist
   ls -la /etc/ssl/tailscale/
   ls -la /var/lib/tailscale/certs/
   
   # Re-run certificate setup
   ./scripts/infrastructure/setup-tailscale-ssl.sh
   ```

4. **Subdomain Certificates Not Generated**
   - Ensure the subdomain is configured in Tailscale admin console
   - Some subdomains may need to be explicitly allowed in Tailscale settings

### Verification Commands

```bash
# Test certificate validity
openssl x509 -in /etc/ssl/tailscale/ubuntuaicodeserver-1.tail5137b4.ts.net.crt -text -noout

# Check certificate expiration
openssl x509 -in /etc/ssl/tailscale/ubuntuaicodeserver-1.tail5137b4.ts.net.crt -noout -dates

# Test HTTPS connectivity
curl -k https://ubuntuaicodeserver-1.tail5137b4.ts.net:10443/
```

## Integration with Platform Services

### Docker Services

Docker services mount the certificate directories:

```yaml
volumes:
  - /opt/tailscale-certs:/etc/ssl/tailscale:ro
  - /var/lib/tailscale/certs:/var/lib/tailscale/certs:ro
```

### Service Access URLs

After SSL setup, services are accessible via:

- **Main Platform**: https://ubuntuaicodeserver-1.tail5137b4.ts.net:10443/
- **Control Panel**: https://ubuntuaicodeserver-1.tail5137b4.ts.net:10443/hub
- **AutoGen Studio**: https://autogen.ubuntuaicodeserver-1.tail5137b4.ts.net/
- **Chat Copilot**: https://copilot.ubuntuaicodeserver-1.tail5137b4.ts.net/
- **VS Code Web**: https://vscode.ubuntuaicodeserver-1.tail5137b4.ts.net/
- And more...

## Security Considerations

1. **Certificate Privacy**: Private keys are stored with restricted permissions (600)
2. **Network Security**: All traffic is encrypted via Tailscale mesh network
3. **Access Control**: Services are only accessible within your tailnet
4. **Certificate Rotation**: Automatic renewal ensures certificates stay current

## Files and Scripts Reference

### Key Scripts
- `/home/keith/chat-copilot/scripts/infrastructure/setup-tailscale-ssl.sh` - Main SSL setup script
- `/home/keith/chat-copilot/scripts/infrastructure/renew-certificates.sh` - Certificate renewal script
- `/home/keith/chat-copilot/scripts/infrastructure/tailscale_https.sh` - Initial Tailscale setup
- `/home/keith/chat-copilot/python/utilities/check-certificates.py` - Certificate monitoring

### Key Configuration Files
- `/home/keith/chat-copilot/nginx-configs/ssl-main.conf` - Main SSL nginx configuration
- `/home/keith/chat-copilot/nginx-configs/*.conf` - Individual service SSL configurations

### Certificate Directories
- `/opt/tailscale-certs/` - Docker/user certificate storage
- `/etc/ssl/tailscale/` - Nginx certificate directory
- `/var/lib/tailscale/certs/` - System Tailscale certificate directory

## Getting Help

If you encounter issues with SSL certificate setup:

1. Check the Tailscale admin console for domain and certificate settings
2. Verify MagicDNS and HTTPS are enabled in Tailscale
3. Run the verification commands to check certificate status
4. Review nginx error logs for specific SSL errors
5. Re-run the setup script with debugging enabled

For more information, refer to:
- [Tailscale HTTPS Documentation](https://tailscale.com/kb/1153/enabling-https/)
- [Nginx SSL Configuration Guide](https://nginx.org/en/docs/http/configuring_https_servers.html)