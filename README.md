# 🚀 LeetCode Activity Tracker

> A production-oriented Python application that tracks multiple LeetCode users, detects newly accepted submissions, persists tracker state using private GitHub Gists, and sends real-time Telegram notifications for competitive programming groups.

<p align="center">

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-88%25%20Coverage-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)
![Ruff](https://img.shields.io/badge/Ruff-Linting-D7FF64?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)

</p>

<p align="center">

![Tests](https://github.com/Akshat-Shukla2004/leetcode-activity-tracker/actions/workflows/tests.yml/badge.svg)

</p>

---

# ✨ Features

- 👥 Track multiple LeetCode users simultaneously
- 📬 Send real-time Telegram notifications for newly accepted submissions
- 🧠 Integrates with the LeetCode GraphQL API
- 📊 Detects only newly accepted submissions to prevent duplicate alerts
- 💾 Persists tracker state using a private GitHub Gist
- 🔄 Prevents duplicate notifications across GitHub Actions runs
- ⚡ Runs automatically every 1 hour using GitHub Actions
- ⚡ Lightweight, modular Python architecture
- 🧪 Comprehensive Pytest suite (~88% test coverage)
- 🎨 Ruff formatting and linting
- 🐳 Docker support for reproducible deployments
- ⚙️ Automated GitHub Actions workflow
- 🔧 Manual workflow trigger for testing and debugging

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
  ┌──────────────────┐          ┌───────────────────────┐
  │ LeetCode GraphQL │          │ GitHub Gist           │
  │       API        │          │ (Persistent State)    │
  └──────────────────┘          └───────────────────────┘
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
├── LICENSE
├── README.md
└── main.py
```

---

# 🛠️ Tech Stack

| Category | Technology |
|-----------|------------|
| Language | Python 3.11 |
| API | LeetCode GraphQL |
| Notifications | Telegram Bot API |
| Persistent Storage | GitHub Gist API |
| Testing | Pytest |
| Code Quality | Ruff |
| Automation | GitHub Actions |
| Containerization | Docker |

---

# ✅ Quality Assurance

- 65 automated tests with 88% coverage using Pytest
- Persistent state across GitHub Actions runs using GitHub Gists
- Ruff linting and code formatting
- Continuous Integration using GitHub Actions
- Dockerized runtime for consistent deployments
- Modular architecture with separated tracking, storage, notification, and messaging components

---

# 🚀 Getting Started

## Clone the Repository

```bash
git clone https://github.com/Akshat-Shukla2004/leetcode-activity-tracker.git

cd leetcode-activity-tracker
```

---

## Create a Virtual Environment

### Linux / macOS

```bash
python -m venv .venv

source .venv/bin/activate
```

### Windows

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

Create a `.env` file in the project root.

```env
BOT_TOKEN=your_telegram_bot_token
CHAT_ID=your_telegram_chat_id

GIST_ID=your_private_gist_id
GIST_TOKEN=your_github_personal_access_token

MY_USERNAME=AkshatPrep
OPPONENT_USERNAMES=user1,user2,user3
```

The application validates `BOT_TOKEN`, `CHAT_ID`, `GIST_ID`, and `GIST_TOKEN` during startup.

`MY_USERNAME` and `OPPONENT_USERNAMES` are optional and fall back to the defaults defined in `backend/config.py`.

---

## Run the Application

```bash
python main.py
```

---

# 🐳 Docker

Docker provides an isolated and reproducible runtime environment, ensuring identical behavior across local development and production deployments.

## Build the Image

```bash
docker build -t leetcode-activity-tracker .
```

## Run (Linux/macOS)

```bash
docker run --rm \
--env-file .env \
leetcode-activity-tracker
```

## Run (Windows PowerShell)

```powershell
docker run --rm `
--env-file .env `
leetcode-activity-tracker
```

Tracker state is persisted in a private GitHub Gist, allowing Docker containers and GitHub Actions runners to remain completely stateless.

---

# 🧪 Testing

Run the full test suite:

```bash
pytest
```

Run tests with coverage:

```bash
coverage run -m pytest

coverage report -m
```

Run Ruff linting:

```bash
ruff check .
```

Automatically format the codebase:

```bash
ruff format .
```

---

# ⚙️ GitHub Actions

The repository includes a GitHub Actions workflow that automatically:

- Installs project dependencies
- Runs Ruff linting
- Executes the complete Pytest suite
- Verifies code quality before changes are merged

A scheduled GitHub Actions workflow runs every 1 hour, persists tracker state using a private GitHub Gist, and prevents duplicate notifications across workflow executions.

---

# 📈 Future Improvements

- PostgreSQL or Redis persistence for multi-instance deployments
- Configurable notification templates
- Support for additional notification providers
- Web dashboard for managing tracked users
- REST API for runtime configuration
- Multi-platform competitive programming support (Codeforces, AtCoder, etc.)

---

# 🤝 Contributing

Contributions, issues, and feature requests are welcome.

To contribute:

1. Fork the repository.
2. Create a feature branch.
3. Make your changes.
4. Run the full test suite.
5. Run Ruff linting and formatting.
6. Submit a Pull Request.

Please ensure all tests pass before opening a pull request.

---

# 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.