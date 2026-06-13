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
    url = "https://kenkoooo.com/atcoder/resources/contests.json"
    try:
        data = requests.get(url, timeout=10).json()
        now_ts = datetime.now(tz=timezone.utc).timestamp()
        contests = []
        for c in data:
            if c["start_epoch_second"] < now_ts:
                continue
            start = _utc_to_ist(c["start_epoch_second"])
            end = _utc_to_ist(
                c["start_epoch_second"] + c["duration_second"])
            contests.append({
                "platform": "AtCoder",
                "name": c["title"],
                "start": start,
                "end": end,
                "url": f"https://atcoder.jp/contests/{c['id']}",
            })
        return contests
    except Exception as e:
        print(f"[AtCoder] Error: {e}")
        return []


# ─────────────────────────────────────────────
# CodeChef  (kontests.net aggregator)
# ─────────────────────────────────────────────
def fetch_codechef() -> list[dict]:
    return _fetch_kontests("codechef.com")


# ─────────────────────────────────────────────
# HackerEarth + HackerRank  (kontests.net)
# ─────────────────────────────────────────────
def fetch_hackerearth() -> list[dict]:
    return _fetch_kontests("hackerearth.com")


def fetch_hackerrank() -> list[dict]:
    return _fetch_kontests("hackerrank.com")


def _fetch_kontests(host: str) -> list[dict]:
    """
    kontests.net is a free aggregator with a simple REST API.
    Endpoint: GET /api?site=<host>
    """
    url = f"https://kontests.net/api/v1/{host.split('.')[0]}"
    try:
        data = requests.get(url, timeout=10).json()
        contests = []
        for c in data:
            if c.get("status") == "BEFORE" or c.get("status") == "CODING":
                start_str = c.get("start_time", "")
                end_str = c.get("end_time", "")
                try:
                    start = datetime.fromisoformat(
                        start_str.replace("Z", "+00:00")).astimezone(IST)
                    end = datetime.fromisoformat(
                        end_str.replace("Z", "+00:00")).astimezone(IST)
                except Exception:
                    continue
                contests.append({
                    "platform": host.split(".")[0].capitalize(),
                    "name": c.get("name", "Unknown"),
                    "start": start,
                    "end": end,
                    "url": c.get("url", ""),
                })
        return contests
    except Exception as e:
        print(f"[{host}] Error: {e}")
        return []


# ─────────────────────────────────────────────
# Aggregate all platforms
# ─────────────────────────────────────────────
def fetch_all_contests() -> list[dict]:
    fetchers = [
        fetch_codeforces,
        fetch_leetcode,
        fetch_atcoder,
        fetch_codechef,
        fetch_hackerearth,
        fetch_hackerrank,
    ]
    all_contests = []
    for fn in fetchers:
        results = fn()
        print(f"  ✓ {fn.__name__.replace('fetch_', '').capitalize()}: "
              f"{len(results)} upcoming contest(s)")
        all_contests.extend(results)

    # Sort by start time
    all_contests.sort(key=lambda c: c["start"])
    return all_contests
