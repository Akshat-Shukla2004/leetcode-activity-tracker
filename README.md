# 🚀 LeetCode Competition Bot

> A production-oriented Python bot that tracks multiple LeetCode users, detects newly accepted submissions, and sends real-time Telegram notifications to keep competitive programming groups engaged.

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
- 📬 Real-time Telegram notifications for newly accepted submissions
- 🧠 Uses the LeetCode GraphQL API
- 📊 Detects only newly accepted submissions (prevents duplicate alerts)
- 💾 Persistent local state between executions
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
  │       API        │          │ (data.json)      │
  └──────────────────┘          └──────────────────┘
             │
             ▼
  ┌─────────────────────────────┐
  │ Duplicate Submission Filter │
  └──────────────┬──────────────┘
                 ▼
      ┌────────────────────────┐
      │ Telegram Bot API       │
      └────────────────────────┘
```

---

# 📂 Project Structure

```text
.
├── backend/
│   ├── __init__.py
│   ├── config.py
│   ├── leetcode.py
│   ├── messages.py
│   ├── notifier.py
│   ├── storage.py
│   └── tracker.py
│
├── tests/
│
├── .github/
│   └── workflows/
│
├── Dockerfile
├── requirements.txt
├── main.py
└── README.md
```

---

# 🛠 Tech Stack

| Category | Technology |
|-----------|------------|
| Language | Python 3.11 |
| API | LeetCode GraphQL |
| Notifications | Telegram Bot API |
| Testing | Pytest |
| Linting | Ruff |
| Automation | GitHub Actions |
| Containerization | Docker |

---

# ✅ Quality Assurance

- ~90% automated test coverage using Pytest
- Ruff linting and formatting
- GitHub Actions continuous integration
- Dockerized runtime for reproducible deployments
- Modular architecture with separated tracking, storage, notification, and messaging components

---

# 🚀 Getting Started

## Clone

```bash
git clone https://github.com/Akshat-Shukla2004/lc-competition-bot.git

cd lc-competition-bot
```

---

## Create a Virtual Environment

Linux/macOS

```bash
python -m venv .venv

source .venv/bin/activate
```

Windows

```powershell
python -m venv .venv

.venv\Scripts\activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configuration

Create a `.env` file.

```env
BOT_TOKEN=your_telegram_bot_token
CHAT_ID=your_telegram_chat_id

# Optional
MY_USERNAME=AkshatPrep
OPPONENT_USERNAMES=user1,user2,user3
```

The application validates `BOT_TOKEN` and `CHAT_ID` during startup.

`MY_USERNAME` and `OPPONENT_USERNAMES` are optional and fall back to the defaults defined in `backend/config.py`.

---

## Run

```bash
python main.py
```

---

# 🐳 Docker

Docker provides an isolated and reproducible runtime environment, ensuring the bot behaves consistently across development and production systems.

## Build

```bash
docker build -t lc-competition-bot .
```

## Run (Linux/macOS)

```bash
docker run --rm \
-v "$(pwd)/data.json:/app/data.json" \
--env-file .env \
lc-competition-bot
```

## Run (Windows PowerShell)

```powershell
docker run --rm `
-v "${PWD}/data.json:/app/data.json" `
--env-file .env `
lc-competition-bot
```

The bind mount ensures that `data.json` persists between container runs so the bot remembers previously processed submissions.

---

# 🧪 Testing

Run the complete test suite:

```bash
pytest
```

Run with coverage:

```bash
coverage run -m pytest

coverage report -m
```

Run Ruff linting:

```bash
ruff check .
```

Format the codebase:

```bash
ruff format .
```

---

# ⚙️ GitHub Actions

The repository includes an automated GitHub Actions workflow that:

- Installs project dependencies
- Runs Ruff linting
- Executes the complete Pytest suite
- Validates code quality before changes are merged

The project can also be executed on a scheduled GitHub Actions workflow to periodically check for new accepted submissions. Since GitHub Actions uses best-effort scheduling, actual execution timing may vary.

---

# 📈 Future Improvements

- PostgreSQL persistence for multi-instance deployments
- Configurable notification templates
- Support for additional notification providers
- Web dashboard for user management
- REST API for managing tracked users

---

# 🤝 Contributing

Contributions, issues, and feature requests are welcome.

If you'd like to contribute:

1. Fork the repository.
2. Create a feature branch.
3. Make your changes.
4. Run the test suite and Ruff checks.
5. Open a Pull Request.

Please ensure all tests pass before submitting changes.

---

# 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for more information.