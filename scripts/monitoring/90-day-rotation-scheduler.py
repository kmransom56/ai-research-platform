#!/usr/bin/env python3
"""
90-Day API Key Rotation Scheduler
Helps schedule and track regular key rotations for security
"""

import datetime
import json
from pathlib import Path

class RotationScheduler:
    def __init__(self):
        self.schedule_file = Path("logs/monitoring/rotation_schedule.json")
        self.schedule_file.parent.mkdir(exist_ok=True)
        
    def initialize_schedule(self):
        """Initialize rotation schedule for all services"""
        today = datetime.date.today()
        
        # Services and their current rotation date (today, since we just rotated)
        services = [
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY", 
            "AZURE_OPENAI_KEY",
            "GEMINI_API_KEY",
            "GH_TOKEN",
            "MERAKI_API_KEY",
            "BRAVE_API_KEY",
            "GROQ_API_KEY",
            "HF_API_KEY"
        ]
        
        schedule = {
            "created": today.isoformat(),
            "rotation_interval_days": 90,
            "services": {}
        }
        
        for service in services:
            next_rotation = today + datetime.timedelta(days=90)
            schedule["services"][service] = {
                "last_rotated": today.isoformat(),
                "next_rotation": next_rotation.isoformat(),
                "rotation_count": 1,
                "status": "rotated_today"
            }
        
        # Save schedule
        with open(self.schedule_file, 'w') as f:
            json.dump(schedule, f, indent=2)
        
        return schedule
    
    def check_upcoming_rotations(self, days_ahead=14):
        """Check for rotations needed in the next N days"""
        if not self.schedule_file.exists():
            print("⚠️  No rotation schedule found. Run --initialize first")
            return []
        
        with open(self.schedule_file) as f:
            schedule = json.load(f)
        
        today = datetime.date.today()
        cutoff_date = today + datetime.timedelta(days=days_ahead)
        
        upcoming = []
        for service, data in schedule["services"].items():
            next_rotation = datetime.date.fromisoformat(data["next_rotation"])
            
            if next_rotation <= cutoff_date:
                days_until = (next_rotation - today).days
                upcoming.append({
                    "service": service,
                    "next_rotation": next_rotation.isoformat(),
                    "days_until": days_until,
                    "status": "overdue" if days_until < 0 else "upcoming"
                })
        
        return upcoming
    
    def generate_rotation_calendar(self):
        """Generate a calendar view of upcoming rotations"""
        print("📅 API KEY ROTATION CALENDAR")
        print("=" * 40)
        
        if not self.schedule_file.exists():
            print("❌ No schedule found. Run with --initialize first")
            return
        
        with open(self.schedule_file) as f:
            schedule = json.load(f)
        
        print(f"Schedule created: {schedule['created']}")
        print(f"Rotation interval: {schedule['rotation_interval_days']} days")
        print()
        
        # Sort services by next rotation date
        services = []
        for service, data in schedule["services"].items():
            services.append((service, data))
        
        services.sort(key=lambda x: x[1]["next_rotation"])
        
        print("📋 UPCOMING ROTATIONS:")
        today = datetime.date.today()
        
        for service, data in services:
            next_rotation = datetime.date.fromisoformat(data["next_rotation"])
            days_until = (next_rotation - today).days
            last_rotated = data["last_rotated"]
            
            if days_until < 0:
                status = "🔴 OVERDUE"
            elif days_until <= 14:
                status = "🟡 SOON"
            else:
                status = "🟢 OK"
            
            print(f"  {status} {service}")
            print(f"      Next: {next_rotation} ({days_until} days)")
            print(f"      Last: {last_rotated}")
            print()
    
    def mark_rotated(self, service_name):
        """Mark a service as rotated today"""
        if not self.schedule_file.exists():
            print("❌ No schedule found")
            return False
        
        with open(self.schedule_file) as f:
            schedule = json.load(f)
        
        if service_name not in schedule["services"]:
            print(f"❌ Service {service_name} not found in schedule")
            return False
        
        today = datetime.date.today()
        next_rotation = today + datetime.timedelta(days=schedule["rotation_interval_days"])
        
        schedule["services"][service_name].update({
            "last_rotated": today.isoformat(),
            "next_rotation": next_rotation.isoformat(),
            "rotation_count": schedule["services"][service_name].get("rotation_count", 0) + 1,
            "status": "rotated_today"
        })
        
        # Save updated schedule
        with open(self.schedule_file, 'w') as f:
            json.dump(schedule, f, indent=2)
        
        print(f"✅ {service_name} marked as rotated. Next rotation: {next_rotation}")
        return True
    
    def generate_rotation_commands(self):
        """Generate commands for upcoming rotations"""
        upcoming = self.check_upcoming_rotations(days_ahead=7)
        
        if not upcoming:
            print("✅ No rotations needed in the next 7 days")
            return
        
        print("🔄 ROTATION COMMANDS FOR UPCOMING SERVICES:")
        print("=" * 45)
        
        for item in upcoming:
            service = item["service"]
            days = item["days_until"]
            
            if days <= 0:
                urgency = "🔴 URGENT"
            else:
                urgency = f"📅 {days} days"
            
            print(f"\n{urgency} - {service}:")
            print(f"  1. Generate new key in service dashboard")
            print(f"  2. gh secret set {service} --body \"new_key_value\"")
            print(f"  3. python3 scripts/monitoring/90-day-rotation-scheduler.py --mark-rotated {service}")
            print(f"  4. Test application: docker compose -f docker-compose.portable.yml up -d")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="90-Day API Key Rotation Scheduler")
    parser.add_argument('--initialize', action='store_true', 
                       help='Initialize rotation schedule (run once after mass rotation)')
    parser.add_argument('--check-upcoming', type=int, default=14, metavar='DAYS',
                       help='Check for rotations needed in next N days (default: 14)')
    parser.add_argument('--calendar', action='store_true',
                       help='Show rotation calendar view')
    parser.add_argument('--mark-rotated', metavar='SERVICE',
                       help='Mark a service as rotated today')
    parser.add_argument('--commands', action='store_true',
                       help='Generate rotation commands for upcoming rotations')
    
    args = parser.parse_args()
    
    scheduler = RotationScheduler()
    
    if args.initialize:
        print("📅 Initializing 90-day rotation schedule...")
        schedule = scheduler.initialize_schedule()
        print(f"✅ Schedule created for {len(schedule['services'])} services")
        print("📋 Next rotations scheduled for:", 
              (datetime.date.today() + datetime.timedelta(days=90)).isoformat())
        print("\nUse --calendar to view the full schedule")
        
    elif args.mark_rotated:
        scheduler.mark_rotated(args.mark_rotated)
        
    elif args.commands:
        scheduler.generate_rotation_commands()
        
    elif args.calendar:
        scheduler.generate_rotation_calendar()
        
    else:
        # Default: check upcoming rotations
        upcoming = scheduler.check_upcoming_rotations(args.check_upcoming)
        
        if upcoming:
            print(f"⚠️  {len(upcoming)} services need rotation in next {args.check_upcoming} days:")
            for item in upcoming:
                status_icon = "🔴" if item["status"] == "overdue" else "🟡"
                print(f"  {status_icon} {item['service']} - {item['days_until']} days")
        else:
            print(f"✅ No rotations needed in next {args.check_upcoming} days")

if __name__ == "__main__":
    main()