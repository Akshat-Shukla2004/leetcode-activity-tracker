"""
storage.py - JSON-based persistence layer.

Handles reading and writing data.json, which stores:
  - last seen submission timestamps per user
  - daily solve counts (user + opponents)
  - streak data
  - historical daily progress
"""

import json
import logging
import os
from datetime import date

from backend import config

logger = logging.getLogger(__name__)


# ─── Schema helpers ───────────────────────────────────────────────────────────

def _empty_user_record() -> dict:
    """Default state for a newly tracked user."""
    return {
        "last_submission_ts": 0,   # Unix timestamp of last seen accepted submission
        "streak": 0,               # Consecutive days with ≥1 solve
        "last_solve_date": "",     # ISO date string of last solve (for streak logic)
        "daily_solves": {},        # { "YYYY-MM-DD": count }
    }


def _default_data() -> dict:
    """Scaffold for a brand-new data.json."""
    return {
        "users": {},      # username → user_record
        "history": [],    # [ { "date": "YYYY-MM-DD", "solves": { username: count } } ]
    }


# ─── Load / Save ─────────────────────────────────────────────────────────────

def load() -> dict:
    """Load data.json; return default scaffold if file is missing or corrupt."""
    if not os.path.exists(config.DATA_FILE):
        logger.info("data.json not found — starting fresh.")
        return _default_data()

    try:
        with open(config.DATA_FILE, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        # Ensure top-level keys always exist (forward-compat with old files)
        data.setdefault("users", {})
        data.setdefault("history", [])
        return data
    except (json.JSONDecodeError, OSError) as exc:
        logger.error("Failed to load data.json (%s) — starting fresh.", exc)
        return _default_data()


def save(data: dict) -> None:
    """Atomically write data to data.json."""
    try:
        tmp_path = config.DATA_FILE + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
        os.replace(tmp_path, config.DATA_FILE)
        logger.debug("data.json saved successfully.")
    except OSError as exc:
        logger.error("Failed to save data.json: %s", exc)


# ─── Per-user helpers ─────────────────────────────────────────────────────────

def get_user(data: dict, username: str) -> dict:
    """Return (and auto-create) the state record for a username."""
    if username not in data["users"]:
        data["users"][username] = _empty_user_record()
    return data["users"][username]


def set_last_submission_ts(data: dict, username: str, ts: int) -> None:
    get_user(data, username)["last_submission_ts"] = ts


def get_last_submission_ts(data: dict, username: str) -> int:
    return get_user(data, username).get("last_submission_ts", 0)


# ─── Daily solve tracking ─────────────────────────────────────────────────────

def increment_daily_solves(data: dict, username: str) -> int:
    """
    Increment today's solve count for username.
    Returns the updated daily count.
    """
    today = date.today().isoformat()
    user = get_user(data, username)
    daily = user.setdefault("daily_solves", {})
    daily[today] = daily.get(today, 0) + 1
    return daily[today]


def get_daily_solves(data: dict, username: str, day: str | None = None) -> int:
    """Return solve count for a specific day (default: today)."""
    day = day or date.today().isoformat()
    return get_user(data, username).get("daily_solves", {}).get(day, 0)


# ─── Streak tracking ──────────────────────────────────────────────────────────

def update_streak(data: dict, username: str) -> int:
    """
    Update the streak counter for username based on today's activity.
    Call this after recording a new solve.
    Returns the current streak count.
    """
    from datetime import timedelta

    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()

    user = get_user(data, username)
    last_date = user.get("last_solve_date", "")

    if last_date == today:
        # Already counted today — streak unchanged
        pass
    elif last_date == yesterday:
        # Consecutive day — extend streak
        user["streak"] = user.get("streak", 0) + 1
    else:
        # Gap or first ever solve — reset to 1
        user["streak"] = 1

    user["last_solve_date"] = today
    return user["streak"]


def get_streak(data: dict, username: str) -> int:
    return get_user(data, username).get("streak", 0)


# ─── History (for future graphs) ─────────────────────────────────────────────

def record_history(data: dict, usernames: list[str]) -> None:
    """
    Append today's solve counts to the history list.
    Safe to call multiple times per day — updates the existing entry if present.
    """
    today = date.today().isoformat()
    solves = {u: get_daily_solves(data, u) for u in usernames}

    # Update existing entry for today if it exists
    for entry in data["history"]:
        if entry.get("date") == today:
            entry["solves"] = solves
            return

    # Otherwise append a new entry
    data["history"].append({"date": today, "solves": solves})

    # Keep only the last 90 days to avoid unbounded growth
    data["history"] = data["history"][-90:]
