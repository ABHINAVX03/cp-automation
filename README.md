# 🏆 CP Contest Tracker

Automatically fetches upcoming contests from **Codeforces, LeetCode, AtCoder, CodeChef, HackerEarth, HackerRank** and adds them to your **Google Calendar** with a **10-minute phone notification** before each contest starts.

---

## 📁 File Structure

```
cp-contest-tracker/
├── main.py           ← Run this to sync contests
├── scheduler.py      ← Run this for automatic daily sync
├── fetcher.py        ← Contest fetching logic (all platforms)
├── calendar_sync.py  ← Google Calendar integration
├── requirements.txt  ← Python dependencies
└── README.md
```

---

## ⚙️ Setup (One-Time — ~10 minutes)

### Step 1 — Install Python dependencies

```bash
pip install -r requirements.txt
```

---

### Step 2 — Set up Google Calendar API

1. Go to [https://console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project (e.g., `CP Tracker`)
3. Go to **APIs & Services → Enable APIs**
4. Search for and enable **Google Calendar API**
5. Go to **APIs & Services → Credentials**
6. Click **Create Credentials → OAuth 2.0 Client ID**
7. Application type: **Desktop app** → Name it anything → Click Create
8. Download the JSON file → **rename it to `credentials.json`**
9. Place `credentials.json` in the same folder as `main.py`

---

### Step 3 — First Run (OAuth Login)

```bash
python main.py
```

- A browser window will open asking you to log in with Google
- Allow access to Google Calendar
- A `token.pickle` file is saved — you won't need to log in again

✅ You'll see a new calendar called **"🏆 CP Contests"** in your Google Calendar!

---

## 🚀 Usage

### Manual sync (run whenever you want)
```bash
python main.py
```

### Preview contests without adding to calendar
```bash
python main.py --dry-run
```

### Just list upcoming contests in terminal
```bash
python main.py --list
```

### Automatic daily sync (runs at 8:00 AM IST every day)
```bash
python scheduler.py
```
> To change the sync time, edit `SYNC_TIME = "08:00"` in `scheduler.py`

---

## 📱 Enable Phone Notifications

The tool sets a **10-minute popup alert** on every contest event. To get it as a phone notification:

1. Install **Google Calendar** app on your phone
2. Go to **Settings → [Your account] → Notifications**
3. Enable **Events** notifications
4. Make sure your phone **Do Not Disturb** settings allow Google Calendar

That's it! You'll get a phone buzz 10 minutes before every contest. 🎯

---

## 🤖 Run Automatically on Startup (Optional)

### Linux / Mac — using cron:
```bash
crontab -e
```
Add this line (syncs every day at 8 AM):
```
0 8 * * * cd /path/to/cp-contest-tracker && python main.py >> sync.log 2>&1
```

### Windows — Task Scheduler:
1. Open Task Scheduler → Create Basic Task
2. Trigger: Daily at 8:00 AM
3. Action: Start a program → `python`
4. Arguments: `C:\path\to\cp-contest-tracker\main.py`

---

## 🎨 Calendar Color Coding

Each platform gets its own color in Google Calendar:
- 🔵 **Codeforces** — Blueberry
- 🟡 **LeetCode** — Banana  
- 🟢 **AtCoder** — Sage
- 🟠 **CodeChef** — Tangerine
- 🟣 **HackerEarth** — Grape
- 🩷 **HackerRank** — Flamingo

---

## 🔔 Reminders Set Per Contest

| Type | Time Before Contest |
|------|-------------------|
| 📳 Phone popup | **10 minutes** |
| 🔔 Phone popup | **1 hour** |
| 📧 Email | **1 hour** |

---

## ❓ Troubleshooting

| Problem | Fix |
|---------|-----|
| `credentials.json not found` | Download OAuth JSON from Google Cloud Console |
| Browser doesn't open for auth | Run `python main.py` in a terminal, not an IDE |
| No contests showing | Check internet; some platforms may be temporarily down |
| Duplicate events | The tool auto-detects duplicates — safe to re-run anytime |
| Token expired | Delete `token.pickle` and re-run `main.py` |
 
