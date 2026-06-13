#!/usr/bin/env python3
"""
Automatic Scheduler
───────────────────
Runs the sync once a day at a configured time using the built-in
`schedule` library — no cron setup needed.

Usage:
    pip install schedule
    python scheduler.py          # runs forever, syncs daily at 08:00 IST
    python scheduler.py --now    # run once immediately then exit
"""

import argparse
import time
import schedule
from datetime import datetime
from zoneinfo import ZoneInfo

from fetcher import fetch_all_contests
from calendar_sync import sync_contests

IST = ZoneInfo("Asia/Kolkata")
SYNC_TIME = "08:00"   # ← change this to your preferred daily sync time


def run_sync():
    now = datetime.now(IST).strftime("%Y-%m-%d %H:%M IST")
    print(f"\n[{now}] ⏰ Starting scheduled CP contest sync …\n")
    contests = fetch_all_contests()
    sync_contests(contests)
    print(f"[{now}] ✅ Sync complete.\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--now", action="store_true",
                        help="Sync once immediately and exit")
    args = parser.parse_args()

    if args.now:
        run_sync()
        return

    print(f"🗓  Scheduler started — will sync every day at {SYNC_TIME} IST")
    print("   Press Ctrl+C to stop.\n")

    schedule.every().day.at(SYNC_TIME).do(run_sync)

    # Run once at startup so you get results immediately
    run_sync()

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
