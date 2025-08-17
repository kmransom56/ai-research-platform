#!/bin/bash

# =============================================================================
# Start 24-48 Hour API Monitoring
# =============================================================================

echo "🚀 STARTING API USAGE MONITORING"
echo "================================="
echo

# Create logs directory
mkdir -p logs/monitoring

# Initial baseline check
echo "📊 Running initial API usage baseline check..."
python3 scripts/monitoring/track-api-usage.py

# Show dashboard
echo
python3 scripts/monitoring/dashboard.py

echo
echo "🔄 Starting background monitoring daemon..."
echo "This will run for 48 hours, checking every 30 minutes"
echo

# Start monitoring in background
nohup bash scripts/monitoring/monitor-daemon.sh > logs/monitoring/daemon.log 2>&1 &
DAEMON_PID=$!

echo "✅ Monitoring daemon started (PID: $DAEMON_PID)"
echo "📝 Daemon log: logs/monitoring/daemon.log"
echo
echo "📋 MONITORING COMMANDS:"
echo "• View dashboard:    python3 scripts/monitoring/dashboard.py"
echo "• Check alerts:      python3 scripts/monitoring/check-alerts.py" 
echo "• Stop monitoring:   pkill -f monitor-daemon.sh"
echo "• View logs:         tail -f logs/monitoring/daemon.log"
echo
echo "🚨 IMPORTANT: Monitor these dashboards manually as well:"
echo "• OpenAI Usage: https://platform.openai.com/usage"
echo "• Azure Costs: https://portal.azure.com/#view/Microsoft_Azure_CostManagement"
echo "• GitHub API Limits: https://github.com/settings/personal-access-tokens"
echo

echo "PID:$DAEMON_PID" > logs/monitoring/daemon.pid
echo "⏰ Monitoring will run for 48 hours. Check back periodically!"
