#!/bin/bash
# AI Research Platform Simple Startup Script
# Simplified startup for new v4.0 system

echo "🚀 AI Research Platform - Simple Startup"
echo "========================================"
echo ""

echo "⚠️  NOTICE: This is a simplified startup script for v4.0 system"
echo ""

# Check if quick-restore exists
RESTORE_SCRIPT="/home/keith/chat-copilot/config-backups-working/latest/quick-restore.sh"

if [[ -f "$RESTORE_SCRIPT" ]]; then
    echo "✅ Found quick-restore script"
    echo "🔄 Running platform restoration..."
    echo ""
    
    if bash "$RESTORE_SCRIPT"; then
        echo ""
        echo "✅ Platform startup completed successfully!"
        echo ""
        echo "🌐 Access your services:"
        echo "   • Control Panel: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/hub"
        echo "   • Chat Copilot: http://100.123.10.72:11000"
        echo "   • AutoGen Studio: http://100.123.10.72:11001"
        echo ""
        echo "📊 Check status: ./check-platform-status.sh"
    else
        echo ""
        echo "❌ Platform startup failed!"
        echo "💡 Try manual recovery:"
        echo "   1. Check logs in /home/keith/chat-copilot/logs/"
        echo "   2. Run: ./check-platform-status.sh"
        echo "   3. Contact support if issues persist"
    fi
else
    echo "❌ Quick-restore script not found at: $RESTORE_SCRIPT"
    echo ""
    echo "💡 This means the backup system needs to be initialized."
    echo "   1. Create a backup: ./scripts/backup-working-config.sh"
    echo "   2. Then run this script again"
    echo ""
    echo "📋 Alternative startup methods:"
    echo "   • ./scripts/platform-management/startup-platform.sh (legacy)"
    echo "   • ./scripts/platform-management/manage-platform.sh start"
fi

echo ""
echo "========================================"