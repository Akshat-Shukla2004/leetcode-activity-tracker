# 🏆 LeetCode Competition Tracker

A fully automated, free-to-run bot that monitors your LeetCode opponent's activity and sends psychologically engaging Telegram alerts — every 5 minutes via GitHub Actions.

---

## 🗂️ Project Structure

```
leetcode_tracker/
├── main.py           ← Entry point
├── config.py         ← Environment config + validation
├── leetcode.py       ← LeetCode GraphQL API client
├── tracker.py        ← Core event detection logic
├── notifier.py       ← Telegram alert system
├── messages.py       ← Dynamic psychological message engine
├── storage.py        ← JSON persistence layer
├── data.json         ← State file (auto-managed)
├── requirements.txt
└── .github/
    └── workflows/
        └── run.yml   ← GitHub Actions (every 5 min)
```

---

## ⚡ Quick Start (Local)

### 1. Clone & install

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
pip install -r requirements.txt
```

### 2. Set environment variables

```bash
export BOT_TOKEN="your_telegram_bot_token"
export CHAT_ID="your_telegram_chat_id"
export MY_USERNAME="your_leetcode_username"
export OPPONENT_USERNAMES="opponent1,opponent2"   # comma-separated
```

### 3. Run

```bash
# Normal competition check
python main.py

# Send daily leaderboard
python main.py leaderboard
```

---

## 🤖 Telegram Bot Setup

1. Open Telegram → search `@BotFather`
2. Send `/newbot` → follow prompts → copy the **BOT_TOKEN**
3. Start a conversation with your new bot
4. Visit `https://api.telegram.org/bot<BOT_TOKEN>/getUpdates`
5. Send yourself a message and grab the **chat_id** from the JSON response

---

## 🚀 GitHub Actions Deployment

### 1. Push your code to a GitHub repo

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### 2. Add Secrets

Go to your repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these secrets:

| Secret Name          | Value                              |
|----------------------|------------------------------------|
| `BOT_TOKEN`          | Your Telegram bot token            |
| `CHAT_ID`            | Your Telegram chat ID              |
| `MY_USERNAME`        | Your LeetCode username             |
| `OPPONENT_USERNAMES` | `opponent1` or `alice,bob`        |

### 3. Enable Actions

Go to **Actions** tab → click **Enable GitHub Actions**

The workflow runs every 5 minutes automatically. You can also trigger it manually via the **workflow_dispatch** button.

> ⚠️ GitHub may delay scheduled runs by a few minutes during high-traffic periods. This is normal.

---

## 🧠 How It Works

### Event-based detection
- Fetches the latest **accepted** submission per opponent
- Compares timestamp to last-seen in `data.json`
- Only fires an alert if the timestamp is **newer** — never on count changes
- Zero duplicate alerts

### Telegram alerts
- Each new accepted solve sends one notification with the full message body
- No bait or decoy messages are sent

### Message intensity scaling
| User inactive | Message tier |
|---|---|
| < 15 min | Standard rotation (all categories) |
| 15–29 min | Aggressive + Time urgency |
| ≥ 30 min | Nuclear tier |
| Opponent streak ≥ 3 | Streak callout emphasis |

### State persistence
GitHub Actions `cache` stores `data.json` between runs so state survives across executions.

---

## 📊 Daily Leaderboard

Sent automatically at 20:00 UTC each day. Shows:
- Today's solve count for you and each opponent
- Current streak (🔥) per user
- Ranked by daily solves

---

## 🔧 Configuration

All configuration is in `config.py` via environment variables.

| Variable | Description | Default |
|---|---|---|
| `BOT_TOKEN` | Telegram bot token | required |
| `CHAT_ID` | Telegram chat ID | required |
| `MY_USERNAME` | Your LeetCode username | `your_username` |
| `OPPONENT_USERNAMES` | Comma-separated opponent usernames | `opponent_username` |
| `INACTIVITY_ESCALATION_MINUTES` | Minutes before nuclear messages | `30` (in config.py) |

---

## 💡 Tips

- The `data.json` is automatically managed — don't edit it manually unless resetting state
- To **reset** an opponent's baseline (so next run picks up their latest solve fresh), delete their entry from `data.json`
- To add a new opponent, just add their username to `OPPONENT_USERNAMES` — state is auto-created
- Runs are completely free within GitHub's generous free tier (2,000 minutes/month for public repos; unlimited for public)
