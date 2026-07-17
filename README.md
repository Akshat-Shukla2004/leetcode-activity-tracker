# 🏆 LeetCode Competition Tracker
[![Backend Tests](https://github.com/Akshat-Shukla2004/lc-competition-bot/actions/workflows/tests.yml/badge.svg)](https://github.com/Akshat-Shukla2004/lc-competition-bot/actions/workflows/tests.yml)

A lightweight Python bot that monitors LeetCode activity, detects newly accepted submissions, and sends Telegram alerts through GitHub Actions scheduled workflows.

---

## ✨ Features

- Track multiple LeetCode users at once
- Detect newly accepted submissions from LeetCode
- Send Telegram notifications for fresh solves
- Persist state between GitHub Actions runs
- Support manual workflow triggers for check and leaderboard modes
- Keep the implementation lightweight and Python-based

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
        └── run.yml   ← GitHub Actions scheduled workflow
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

# Send a leaderboard summary
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

The project runs automatically through GitHub Actions scheduled workflows. Actual execution timing depends on GitHub Actions scheduling. You can also trigger it manually via the **workflow_dispatch** button.

> ⚠️ GitHub scheduled workflows are best-effort and may run later than the configured schedule.

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
| 15–59 min | Aggressive + Time urgency |
| ≥ 60 min | Nuclear tier via inactivity threshold |

### State persistence
GitHub Actions `cache` stores `data.json` between runs so state survives across executions.

---

## 📊 Leaderboard Summary

Available through the `leaderboard` mode. Shows:
- Today's solve count for you and each opponent
- Ranked by daily solves
- Persistent solve totals per tracked user

---

## 🔧 Configuration

All configuration is in `config.py` via environment variables.

| Variable | Description | Default |
|---|---|---|
| `BOT_TOKEN` | Telegram bot token | required |
| `CHAT_ID` | Telegram chat ID | required |
| `MY_USERNAME` | Your LeetCode username | `your_username` |
| `OPPONENT_USERNAMES` | Optional extra opponent usernames to add on top of the built-in list | optional |
| `INACTIVITY_ESCALATION_MINUTES` | Minutes before nuclear messages | `30` (in config.py) |

---

## 💡 Tips

- The `data.json` is automatically managed — don't edit it manually unless resetting state
- To **reset** an opponent's baseline (so next run picks up their latest solve fresh), delete their entry from `data.json`
- To add a new opponent, update the built-in list in `config.py` or append extra usernames via `OPPONENT_USERNAMES` — state is auto-created
- Runs are completely free within GitHub's generous free tier (2,000 minutes/month for public repos; unlimited for public)
