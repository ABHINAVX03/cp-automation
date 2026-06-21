"""
Contest Fetcher — pulls upcoming contests from all CP platforms.
Uses free public APIs; no login required.
"""

import requests
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")


def _utc_to_ist(ts: int) -> datetime:
    """Convert a UTC unix timestamp to an IST-aware datetime."""
    return datetime.fromtimestamp(ts, tz=timezone.utc).astimezone(IST)


# ─────────────────────────────────────────────
# Codeforces  (official API)
# ─────────────────────────────────────────────
def fetch_codeforces() -> list[dict]:
    url = "https://codeforces.com/api/contest.list?gym=false"
    try:
        data = requests.get(url, timeout=10).json()
        if data.get("status") != "OK":
            return []
        contests = []
        for c in data["result"]:
            if c["phase"] != "BEFORE":
                continue
            start = _utc_to_ist(c["startTimeSeconds"])
            end_ts = c["startTimeSeconds"] + c["durationSeconds"]
            end = _utc_to_ist(end_ts)
            contests.append({
                "platform": "Codeforces",
                "name": c["name"],
                "start": start,
                "end": end,
                "url": f"https://codeforces.com/contest/{c['id']}",
            })
        return contests
    except Exception as e:
        print(f"[Codeforces] Error: {e}")
        return []


# ─────────────────────────────────────────────
# LeetCode  (unofficial public endpoint)
# ─────────────────────────────────────────────
def fetch_leetcode() -> list[dict]:
    url = "https://leetcode.com/graphql"
    query = """
    query {
      allContests {
        title
        startTime
        duration
        titleSlug
      }
    }
    """
    try:
        resp = requests.post(
            url,
            json={"query": query},
            headers={"Content-Type": "application/json",
                     "Referer": "https://leetcode.com"},
            timeout=10,
        )
        contests_raw = resp.json()["data"]["allContests"]
        now_ts = datetime.now(tz=timezone.utc).timestamp()
        contests = []
        for c in contests_raw:
            if c["startTime"] < now_ts:
                continue
            start = _utc_to_ist(c["startTime"])
            end = _utc_to_ist(c["startTime"] + c["duration"])
            contests.append({
                "platform": "LeetCode",
                "name": c["title"],
                "start": start,
                "end": end,
                "url": f"https://leetcode.com/contest/{c['titleSlug']}",
            })
        return contests
    except Exception as e:
        print(f"[LeetCode] Error: {e}")
        return []


# ─────────────────────────────────────────────
# AtCoder  (atcoder-problems public API)
# ─────────────────────────────────────────────
def fetch_atcoder() -> list[dict]:
    from bs4 import BeautifulSoup
    from datetime import timedelta

    url = "https://atcoder.jp/contests/?lang=en"
    headers = {"User-Agent": "Mozilla/5.0 (compatible; CP-Bot/1.0)"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        upcoming_div = soup.find("div", id="contest-table-upcoming")
        if not upcoming_div:
            return []

        contests = []
        for row in upcoming_div.find_all("tr")[1:]:   # skip header
            cols = row.find_all("td")
            if len(cols) < 3:
                continue

            time_tag = cols[0].find("time")
            if not time_tag:
                continue
            start_str = time_tag.text.strip()         # ✅ "2026-06-21 19:00:00+0900"

            link = cols[1].find("a")
            if not link:
                continue
            name = link.text.strip()
            contest_url = "https://atcoder.jp" + link["href"]

            duration_str = cols[2].text.strip()       # "04:00"

            try:
                start = datetime.strptime(start_str.strip(), "%Y-%m-%d %H:%M:%S%z")
                start = start.astimezone(IST)
            except Exception:
                continue
            try:
                h, m = map(int, duration_str.split(":"))
                end = start + timedelta(hours=h, minutes=m)
            except Exception:
                end = start + timedelta(hours=2)

            contests.append({
                "platform": "AtCoder",
                "name":     name,
                "start":    start,
                "end":      end,
                "url":      contest_url,
            })

        return contests

    except Exception as e:
        print(f"[AtCoder] Error: {e}")
        return []

# ─────────────────────────────────────────────
# CodeChef  (official API — no auth needed)
# ─────────────────────────────────────────────
def fetch_codechef() -> list[dict]:
    url = "https://www.codechef.com/api/list/contests/all"
    headers = {"User-Agent": "Mozilla/5.0 (compatible; CP-Bot/1.0)"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if data.get("status") != "success":
            return []

        contests = []
        for c in data.get("future_contests", []):
            start_str = c.get("contest_start_date", "")
            end_str   = c.get("contest_end_date",   "")
            try:
                # CodeChef returns IST times: "24 Jun 2026 20:00:00"
                fmt   = "%d %b %Y %H:%M:%S"
                start = datetime.strptime(start_str, fmt).replace(tzinfo=IST)
                end   = datetime.strptime(end_str,   fmt).replace(tzinfo=IST)
            except Exception:
                continue

            contests.append({
                "platform": "CodeChef",
                "name":     c.get("contest_name", "Unknown"),
                "start":    start,
                "end":      end,
                "url":      f"https://www.codechef.com/{c.get('contest_code', '')}",
            })
        return contests

    except Exception as e:
        print(f"[CodeChef] Error: {e}")
        return []

def fetch_all_contests() -> list[dict]:
    fetchers = [
        fetch_codeforces,
        fetch_leetcode,
        fetch_atcoder,
        fetch_codechef,          
    ]
    all_contests = []
    for fn in fetchers:
        results = fn()
        print(f"  ✓ {fn.__name__.replace('fetch_', '').capitalize()}: "
              f"{len(results)} upcoming contest(s)")
        all_contests.extend(results)

    all_contests.sort(key=lambda c: c["start"])
    return all_contests