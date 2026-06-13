#!/usr/bin/env python3
"""
CP Contest Tracker — main entry point
─────────────────────────────────────
Run this script to sync upcoming contests to Google Calendar.

Usage:
    python main.py              # Full sync
    python main.py --dry-run    # Preview without adding to calendar
    python main.py --list       # Just print upcoming contests
"""

import argparse
from fetcher import fetch_all_contests
from calendar_sync import sync_contests


def print_contests(contests):
    if not contests:
        print("No upcoming contests found.")
        return
    print(f"\n{'─'*65}")
    print(f"  {'PLATFORM':<14} {'CONTEST':<32} {'START (IST)'}")
    print(f"{'─'*65}")
    for c in contests:
        name = c["name"][:30] + ".." if len(c["name"]) > 32 else c["name"]
        start = c["start"].strftime("%d %b %Y  %H:%M")
        print(f"  {c['platform']:<14} {name:<32} {start}")
    print(f"{'─'*65}\n")


def main():
    parser = argparse.ArgumentParser(description="CP Contest Tracker")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Fetch contests and print them without touching Google Calendar"
    )
    parser.add_argument(
        "--list", action="store_true",
        help="Only list upcoming contests, no calendar sync"
    )
    args = parser.parse_args()

    print("\n🔍 Fetching contests from all platforms …\n")
    contests = fetch_all_contests()

    print_contests(contests)

    if args.list:
        return

    print("📅 Syncing to Google Calendar …\n")
    sync_contests(contests, dry_run=args.dry_run)

    if not args.dry_run:
        print("\n✅ Done! Open Google Calendar on your phone to see contests.")
        print("   Make sure Google Calendar notifications are enabled "
              "on your phone for the 10-min alerts to work.\n")


if __name__ == "__main__":
    main()
