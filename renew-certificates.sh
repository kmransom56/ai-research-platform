#!/bin/bash
# Tailscale Certificate Renewal Script

LOG_FILE="/var/log/tailscale-cert-renewal.log"
NGINX_CONTAINER="nginx-proxy-manager"

log_message() {
    echo "$(date): $1" >> "$LOG_FILE"
}

log_message "Starting certificate renewal process"

# Renew main certificate
if sudo tailscale cert ubuntuaicodeserver-1.tail5137b4.ts.net; then
    log_message "Main certificate renewed successfully"
else
    log_message "Failed to renew main certificate"
    exit 1
fi

# Renew subdomain certificates

if sudo tailscale cert copilot.ubuntuaicodeserver-1.tail5137b4.ts.net; then
    log_message "Certificate for copilot.ubuntuaicodeserver-1.tail5137b4.ts.net renewed successfully"
else
    log_message "Failed to renew certificate for copilot.ubuntuaicodeserver-1.tail5137b4.ts.net"
fi

if sudo tailscale cert autogen.ubuntuaicodeserver-1.tail5137b4.ts.net; then
    log_message "Certificate for autogen.ubuntuaicodeserver-1.tail5137b4.ts.net renewed successfully"
else
    log_message "Failed to renew certificate for autogen.ubuntuaicodeserver-1.tail5137b4.ts.net"
fi

if sudo tailscale cert magentic.ubuntuaicodeserver-1.tail5137b4.ts.net; then
    log_message "Certificate for magentic.ubuntuaicodeserver-1.tail5137b4.ts.net renewed successfully"
else
    log_message "Failed to renew certificate for magentic.ubuntuaicodeserver-1.tail5137b4.ts.net"
fi

if sudo tailscale cert webhook.ubuntuaicodeserver-1.tail5137b4.ts.net; then
    log_message "Certificate for webhook.ubuntuaicodeserver-1.tail5137b4.ts.net renewed successfully"
else
    log_message "Failed to renew certificate for webhook.ubuntuaicodeserver-1.tail5137b4.ts.net"
fi

if sudo tailscale cert portscanner.ubuntuaicodeserver-1.tail5137b4.ts.net; then
    log_message "Certificate for portscanner.ubuntuaicodeserver-1.tail5137b4.ts.net renewed successfully"
else
    log_message "Failed to renew certificate for portscanner.ubuntuaicodeserver-1.tail5137b4.ts.net"
fi

if sudo tailscale cert nginx-manager.ubuntuaicodeserver-1.tail5137b4.ts.net; then
    log_message "Certificate for nginx-manager.ubuntuaicodeserver-1.tail5137b4.ts.net renewed successfully"
else
    log_message "Failed to renew certificate for nginx-manager.ubuntuaicodeserver-1.tail5137b4.ts.net"
fi

if sudo tailscale cert http-gateway.ubuntuaicodeserver-1.tail5137b4.ts.net; then
    log_message "Certificate for http-gateway.ubuntuaicodeserver-1.tail5137b4.ts.net renewed successfully"
else
    log_message "Failed to renew certificate for http-gateway.ubuntuaicodeserver-1.tail5137b4.ts.net"
fi

if sudo tailscale cert https-gateway.ubuntuaicodeserver-1.tail5137b4.ts.net; then
    log_message "Certificate for https-gateway.ubuntuaicodeserver-1.tail5137b4.ts.net renewed successfully"
else
    log_message "Failed to renew certificate for https-gateway.ubuntuaicodeserver-1.tail5137b4.ts.net"
fi

if sudo tailscale cert vscode.ubuntuaicodeserver-1.tail5137b4.ts.net; then
    log_message "Certificate for vscode.ubuntuaicodeserver-1.tail5137b4.ts.net renewed successfully"
else
    log_message "Failed to renew certificate for vscode.ubuntuaicodeserver-1.tail5137b4.ts.net"
fi

if sudo tailscale cert fortinet.ubuntuaicodeserver-1.tail5137b4.ts.net; then
    log_message "Certificate for fortinet.ubuntuaicodeserver-1.tail5137b4.ts.net renewed successfully"
else
    log_message "Failed to renew certificate for fortinet.ubuntuaicodeserver-1.tail5137b4.ts.net"
fi

if sudo tailscale cert perplexica.ubuntuaicodeserver-1.tail5137b4.ts.net; then
    log_message "Certificate for perplexica.ubuntuaicodeserver-1.tail5137b4.ts.net renewed successfully"
else
    log_message "Failed to renew certificate for perplexica.ubuntuaicodeserver-1.tail5137b4.ts.net"
fi

if sudo tailscale cert searxng.ubuntuaicodeserver-1.tail5137b4.ts.net; then
    log_message "Certificate for searxng.ubuntuaicodeserver-1.tail5137b4.ts.net renewed successfully"
else
    log_message "Failed to renew certificate for searxng.ubuntuaicodeserver-1.tail5137b4.ts.net"
fi

if sudo tailscale cert openwebui.ubuntuaicodeserver-1.tail5137b4.ts.net; then
    log_message "Certificate for openwebui.ubuntuaicodeserver-1.tail5137b4.ts.net renewed successfully"
else
    log_message "Failed to renew certificate for openwebui.ubuntuaicodeserver-1.tail5137b4.ts.net"
fi

# Restart Nginx to load new certificates
if docker restart "$NGINX_CONTAINER"; then
    log_message "Nginx restarted successfully"
else
    log_message "Failed to restart Nginx"
fi

log_message "Certificate renewal process completed"
