#!/bin/bash

# Simple Real-Time Sync Starter
echo "🔄 Starting Real-Time Sync to Backup Server..."
echo "💾 Source: 192.168.0.1 (this server)"
echo "🎮 Backup: 192.168.0.5 (high GPU RAM server)"
echo

# Test connection
if ! ssh -o ConnectTimeout=5 keith-ransom@192.168.0.5 "echo 'connected'" >/dev/null 2>&1; then
    echo "❌ Cannot connect to backup server"
    exit 1
fi

echo "✅ Connection to backup server successful"

# Initial full sync
echo "🔄 Performing initial sync..."
bash scripts/sync/rsync-platform-enhanced.sh push backup-server --include-systemd

echo "👁️  Starting file watcher..."

# Start file watcher
inotifywait -m -r -e modify,create,delete,move \
    --format '%w%f %e' \
    /home/keith/chat-copilot/webapi \
    /home/keith/chat-copilot/webapp \
    /home/keith/chat-copilot/scripts \
    /home/keith/chat-copilot/configs \
    /home/keith/chat-copilot/docker \
    /home/keith/chat-copilot/docs \
    /home/keith/chat-copilot/agents \
    /home/keith/chat-copilot/plugins \
    /home/keith/chat-copilot/tools \
    /home/keith/chat-copilot/python \
    /home/keith/chat-copilot/shared \
    /home/keith/chat-copilot/*.md \
    /home/keith/chat-copilot/*.yml \
    /home/keith/chat-copilot/*.yaml \
    /home/keith/chat-copilot/*.json \
    /home/keith/chat-copilot/*.sh 2>/dev/null | \
while read file event; do
    # Skip temporary files
    case "$file" in
        *.log|*.tmp|*.swp|*.swo|*~|*.pyc|*.pyo|*.lock)
            continue
            ;;
        */.git/*|*/node_modules/*|*/__pycache__/*|*/.venv/*|*/venv/*|*/build/*|*/dist/*|*/target/*|*/bin/*|*/obj/*|*/logs/*|*/pids/*|*/temp/*|*/tmp/*)
            continue
            ;;
    esac
    
    echo "🔄 Syncing: $file ($event)"
    
    # Sync the file
    rsync -avz "$file" "keith-ransom@192.168.0.5:~/chat-copilot/" 2>/dev/null &
    
    # If it's a service file, sync to systemd
    if [[ "$file" == *.service ]]; then
        service_name=$(basename "$file")
        if [[ -f "/etc/systemd/system/$service_name" ]]; then
            rsync -avz "/etc/systemd/system/$service_name" "keith-ransom@192.168.0.5:/tmp/" 2>/dev/null
            ssh keith-ransom@192.168.0.5 "sudo cp /tmp/$service_name /etc/systemd/system/ && sudo systemctl daemon-reload" 2>/dev/null
            echo "🔄 Synced systemd service: $service_name"
        fi
    fi
    
    # Small delay to avoid rapid syncs
    sleep 1
done