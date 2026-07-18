# 🚀 LeetCode Competition Bot

> A production-oriented Python bot that tracks multiple LeetCode users, detects newly accepted submissions, and sends real-time Discord notifications to keep competitive programming groups engaged.

<p align="center">

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-90%25%20Coverage-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)
![Ruff](https://img.shields.io/badge/Ruff-Linting-D7FF64?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)

</p>

<p align="center">

![Tests](https://github.com/Akshat-Shukla2004/lc-competition-bot/actions/workflows/tests.yml/badge.svg)

</p>

---

# ✨ Features

- 👥 Track multiple LeetCode users simultaneously
- 📬 Real-time Discord webhook notifications for newly accepted submissions
- 🧠 Uses LeetCode GraphQL API
- 📊 Detects only new accepted submissions (avoids duplicate alerts)
- 💾 Persistent state across executions
- ⚡ Lightweight Python implementation
- 🧪 Comprehensive Pytest suite (~90% coverage)
- 🎨 Ruff formatting & linting
- 🐳 Docker support
- ⚙️ Automated GitHub Actions workflow
- 🔧 Manual workflow trigger for testing

---

# 📸 Example Notification

```text
🎯 John just solved Two Sum (Easy)

⏰ You were inactive for 21 minutes.

Time to get back to solving!

https://leetcode.com/problems/two-sum/
```

---

# 🏗️ Architecture

```text
                ┌────────────────────┐
                │ GitHub Actions /   │
                │ Docker Container   │
                └──────────┬─────────┘
                           │
                           ▼
                ┌────────────────────┐
                │   Tracker Engine   │
                └──────────┬─────────┘
                           │
            ┌──────────────┴──────────────┐
            ▼                             ▼
 ┌──────────────────┐          ┌──────────────────┐
 │ LeetCode GraphQL │          │ Local State      │
 │      API         │          │ Persistence      │
 └──────────────────┘          └──────────────────┘
            │
            ▼
 ┌─────────────────────────────┐
 │ Duplicate Submission Filter │
 └──────────────┬──────────────┘
                ▼
      ┌─────────────────────┐
      │ Discord Webhook API │
      └─────────────────────┘
```

---

# 📂 Project Structure

```text
.
├── backend/
│   ├── config.py
│   ├── leetcode.py
│   ├── messages.py
│   ├── notifier.py
│   ├── storage.py
│   └── tracker.py
│
├── tests/
│
├── .github/workflows/
│
├── Dockerfile
├── requirements.txt
└── main.py
```

---

# 🛠 Tech Stack

| Category | Technology |
|----------|------------|
| Language | Python 3 |
| Testing | Pytest |
| Formatting | Ruff |
| API | LeetCode GraphQL |
| Notifications | Discord Webhooks |
| Automation | GitHub Actions |
| Containerization | Docker |

---

# 🚀 Getting Started

## Clone

```bash
git clone https://github.com/Akshat-Shukla2004/lc-competition-bot.git

cd lc-competition-bot
```

---

## Install

```bash
python -m venv .venv

source .venv/bin/activate
```

Windows

```powershell
.venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## Configuration

Create a `.env` file

```env
DISCORD_WEBHOOK_URL=your_webhook
LEETCODE_USERS=user1,user2,user3
```

---

## Run

```bash
python main.py
```

---

# Docker

Docker provides a reproducible runtime environment, so the bot behaves the same way in local testing and production deployments.

## Build

```bash
docker build -t lc-competition-bot .
```

## Run

```bash
docker run --rm \
      -e BOT_TOKEN=your_telegram_bot_token \
      -e CHAT_ID=your_telegram_chat_id \
      -e MY_USERNAME=your_leetcode_username \
      -e OPPONENT_USERNAMES=opponent1,opponent2 \
      lc-competition-bot
```

---

# 🧪 Testing

Run the complete test suite

```bash
pytest
```

Run with coverage

```bash
coverage run -m pytest
coverage report -m
```

Lint

```bash
ruff check .
```

Format

```bash
ruff format .
```

---

# ⚙️ GitHub Actions

The repository includes an automated workflow that:

- installs dependencies
- runs Ruff linting
- executes the full Pytest suite
- validates code quality before changes are merged

Scheduled workflows can also be used to automatically check for new submissions. Actual execution timing depends on GitHub Actions scheduling.

---

# 📈 Future Improvements

- PostgreSQL persistence for multi-instance deployments
- Redis caching layer
- Configurable notification templates
- Web dashboard
- Multiple notification providers (Slack, Telegram, Discord)

---

# 🤝 Contributing

Contributions, issues, and feature requests are welcome.

Feel free to fork the repository and submit a pull request.

---

# 📄 License

This project is licensed under the MIT License.