#!/bin/bash
# Tailscale HTTPS Setup Script

# Step 1: Update machine name to "netintegrate"
echo "Updating Tailscale machine name to 'ubuntuaicodeserver-1'..."
sudo tailscale up --hostname=ubuntuaicodeserver-1

# Step 2: Check current status
echo "Current Tailscale status:"
tailscale status

# Step 3: Get your tailnet domain (you'll need this for the next steps)
echo "Your machine should now be accessible as: ubuntuaicodeserver-1.tail5137b4.ts.net"
echo "Check your Tailscale admin console to see the full domain name"

# Step 4: Create directory for certificates
sudo mkdir -p /opt/tailscale-certs
sudo chown $USER:$USER /opt/tailscale-certs
cd /opt/tailscale-certs
tailscale cert ubuntuaicodeserver-1.tail5137b4.ts.net

echo "Next steps:"
echo "1. Go to https://login.tailscale.com/admin/dns"
echo "2. Enable MagicDNS if not already enabled"
echo "3. Under 'HTTPS Certificates', click 'Enable HTTPS'"
echo "4. Note your full domain name (ubuntuaicodeserver-1.tail5137b4.ts.net)"
echo "5. Run the certificate generation script"
