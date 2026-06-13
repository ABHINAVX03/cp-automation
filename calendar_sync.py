"""
Google Calendar Sync
────────────────────
Adds upcoming CP contests to Google Calendar with:
  • a 10-minute popup notification  (phone push if app is set up)
  • a 1-hour email reminder

Requires:  pip install google-auth google-auth-oauthlib google-api-python-client
Credentials: OAuth 2.0 client credentials JSON from Google Cloud Console
"""

import os
import json
import pickle
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar"]
TOKEN_FILE = Path("token.pickle")
CREDS_FILE = Path("credentials.json")

# Calendar name that will be created (or reused) for CP contests
CP_CALENDAR_NAME = "🏆 CP Contests"

# ─── Auth ────────────────────────────────────────────────────────────────────

def get_credentials() -> Credentials:
    creds = None
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDS_FILE.exists():
                raise FileNotFoundError(
                    "credentials.json not found!\n"
                    "Download it from: https://console.cloud.google.com/apis/credentials\n"
                    "Place it next to this script and re-run."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDS_FILE), SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)

    return creds


def get_service():
    creds = get_credentials()
    return build("calendar", "v3", credentials=creds)


# ─── Calendar helpers ─────────────────────────────────────────────────────────

def get_or_create_cp_calendar(service) -> str:
    """Return the calendar ID for the CP calendar; create it if missing."""
    calendars = service.calendarList().list().execute().get("items", [])
    for cal in calendars:
        if cal.get("summary") == CP_CALENDAR_NAME:
            return cal["id"]

    # Create a new calendar
    body = {
        "summary": CP_CALENDAR_NAME,
        "description": "Auto-synced competitive programming contests",
        "timeZone": "Asia/Kolkata",
    }
    created = service.calendars().insert(body=body).execute()
    print(f"  ✓ Created new Google Calendar: '{CP_CALENDAR_NAME}'")
    return created["id"]


def _event_key(contest: dict) -> str:
    """Unique key to detect duplicates (platform + name + start time)."""
    return f"{contest['platform']}::{contest['name']}::{contest['start'].isoformat()}"


def list_existing_events(service, calendar_id: str) -> set[str]:
    """Return a set of event keys already on the calendar."""
    existing = set()
    page_token = None
    while True:
        resp = service.events().list(
            calendarId=calendar_id,
            maxResults=250,
            pageToken=page_token,
            fields="items(summary,start,description),nextPageToken",
        ).execute()
        for ev in resp.get("items", []):
            desc = ev.get("description", "")
            # We embed the key in the description for reliable dedup
            for line in desc.splitlines():
                if line.startswith("KEY::"):
                    existing.add(line[5:])
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return existing


# ─── Core sync ───────────────────────────────────────────────────────────────

PLATFORM_COLORS = {
    # Google Calendar color IDs (1-11)
    "Codeforces":  "9",   # blueberry
    "Leetcode":    "5",   # banana
    "Atcoder":     "2",   # sage
    "Codechef":    "6",   # tangerine
    "Hackerearth": "3",   # grape
    "Hackerrank":  "4",   # flamingo
}


def sync_contests(contests: list[dict], dry_run: bool = False) -> int:
    """
    Add contests to Google Calendar.
    Returns the number of new events created.
    """
    if not contests:
        print("No contests to sync.")
        return 0

    service = get_service()
    calendar_id = get_or_create_cp_calendar(service)
    existing_keys = list_existing_events(service, calendar_id)

    added = 0
    skipped = 0

    for contest in contests:
        key = _event_key(contest)
        if key in existing_keys:
            skipped += 1
            continue

        platform = contest["platform"]
        event_body = {
            "summary": f"[{platform}] {contest['name']}",
            "description": (
                f"Platform: {platform}\n"
                f"Contest URL: {contest['url']}\n"
                f"KEY::{key}"
            ),
            "start": {
                "dateTime": contest["start"].isoformat(),
                "timeZone": "Asia/Kolkata",
            },
            "end": {
                "dateTime": contest["end"].isoformat(),
                "timeZone": "Asia/Kolkata",
            },
            "colorId": PLATFORM_COLORS.get(platform, "1"),
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "popup", "minutes": 10},   # phone notification
                    {"method": "popup", "minutes": 60},   # 1-hour heads up
                    {"method": "email",  "minutes": 60},  # email backup
                ],
            },
            "source": {
                "title": platform,
                "url": contest["url"],
            },
        }

        if dry_run:
            print(f"  [DRY RUN] Would add: {event_body['summary']} "
                  f"@ {contest['start'].strftime('%d %b %Y %H:%M IST')}")
            added += 1
            continue

        try:
            service.events().insert(
                calendarId=calendar_id, body=event_body
            ).execute()
            print(f"  ✓ Added: {event_body['summary']} "
                  f"@ {contest['start'].strftime('%d %b %Y %H:%M IST')}")
            added += 1
        except HttpError as e:
            print(f"  ✗ Failed to add '{contest['name']}': {e}")

    print(f"\n  Summary: {added} added, {skipped} already on calendar.")
    return added
