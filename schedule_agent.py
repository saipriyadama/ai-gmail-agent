import schedule
import time
import subprocess
import json
from datetime import datetime

def run_agent():
    """Run the Gmail agent"""
    print(f"\n{'='*80}")
    print(f"⏰ Running agent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")
    
    subprocess.run(['python', 'gmail_agent_real.py'])
    
    print(f"\n✅ Agent completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

def schedule_agent(interval_minutes=60):
    """Schedule agent to run every X minutes"""
    schedule.every(interval_minutes).minutes.do(run_agent)
    
    print(f"✅ Agent scheduled to run every {interval_minutes} minutes")
    print("Press Ctrl+C to stop\n")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    try:
        schedule_agent(interval_minutes=60)  # Run every hour
    except KeyboardInterrupt:
        print("\n✅ Scheduler stopped")