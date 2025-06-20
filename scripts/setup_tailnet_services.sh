#!/usr/bin/env bash
# setup_tailnet_services.sh  — simplified
# Tailscale Serve supports a single HTTPS listener per node.  We forward that
# listener to Caddy on 127.0.0.1:8080; Caddy then routes by Host header.
#
# Usage:  sudo ./setup_tailnet_services.sh

set -euo pipefail

CADDY_BACKEND="http://127.0.0.1:8080"

# Reset previous Serve config (ignore error if none present)
sudo tailscale serve reset || true

echo "Enabling HTTPS listener on this node …"
# One HTTPS listener (port 443) ➜ local Caddy
sudo tailscale serve --bg "${CADDY_BACKEND}"

echo "Current Serve status:"
tailscale serve status 