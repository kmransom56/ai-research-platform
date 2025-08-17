#!/bin/bash

# =============================================================================
# Monitoring Daemon for 24-48 Hour Period
# =============================================================================

MONITORING_DURATION_HOURS=48
CHECK_INTERVAL_MINUTES=30
LOG_DIR="logs/monitoring"
ALERT_THRESHOLD_FILE="scripts/monitoring/alert_thresholds.json"

mkdir -p "$LOG_DIR"

# Create alert thresholds
cat > "$ALERT_THRESHOLD_FILE" << 'THRESHOLDS'
{
  "github_api_usage_percent": 85,
  "unusual_activity_requests_per_hour": 100,
  "failed_auth_attempts": 5,
  "new_ip_addresses": true
}
THRESHOLDS

echo "🔄 Starting $MONITORING_DURATION_HOURS hour monitoring period..."
echo "📊 Check interval: $CHECK_INTERVAL_MINUTES minutes"
echo "📝 Logs: $LOG_DIR"
echo

START_TIME=$(date +%s)
END_TIME=$((START_TIME + MONITORING_DURATION_HOURS * 3600))

while [ $(date +%s) -lt $END_TIME ]; do
    CURRENT_TIME=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$CURRENT_TIME] Running API usage check..."
    
    # Run usage tracker
    python3 scripts/monitoring/track-api-usage.py
    
    # Log system status
    echo "[$CURRENT_TIME] System Status:" >> "$LOG_DIR/system_status.log"
    docker compose ps >> "$LOG_DIR/system_status.log" 2>/dev/null || echo "Docker not running" >> "$LOG_DIR/system_status.log"
    echo "---" >> "$LOG_DIR/system_status.log"
    
    # Wait for next check
    sleep $((CHECK_INTERVAL_MINUTES * 60))
done

echo "✅ Monitoring period completed after $MONITORING_DURATION_HOURS hours"
