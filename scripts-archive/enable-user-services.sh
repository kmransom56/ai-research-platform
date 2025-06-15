#!/bin/bash
# Enable user services after login
export XDG_RUNTIME_DIR="/run/user/$(id -u)"

# Enable lingering for user services to start at boot
sudo loginctl enable-linger keith

# Start user services
systemctl --user daemon-reload
systemctl --user enable autogen-studio-ai-platform.service
systemctl --user enable webhook-server-ai-platform.service 
systemctl --user enable chat-copilot-backend.service
systemctl --user enable chat-copilot-frontend.service

echo "✅ User services enabled for auto-startup"
