"""
storage.py - GitHub Gist-based persistence layer.

Handles reading and writing application state to a private GitHub Gist,
which stores:
  - last seen submission timestamps per user
  - daily solve counts (user + opponents)
  - historical daily progress
"""

import json
import logging
from datetime import date

import requests

from backend import config

logger = logging.getLogger(__name__)

GIST_FILENAME = "leetcode-state.json"
GIST_API_URL = "https://api.github.com/gists/{gist_id}"
REQUEST_TIMEOUT = 15


def _empty_user_record() -> dict:
    return {
        "last_submission_ts": 0,
        "daily_solves": {},
    }


def _clean_user_record(record: dict) -> dict:
    cleaned = _empty_user_record()
    cleaned["last_submission_ts"] = record.get("last_submission_ts", 0)

    daily = record.get("daily_solves", {})
    cleaned["daily_solves"] = daily if isinstance(daily, dict) else {}

    return cleaned


def _default_data() -> dict:
    return {
        "users": {},
        "history": [],
    }


def _gist_url() -> str:
    return GIST_API_URL.format(gist_id=config.GIST_ID)


def _gist_headers() -> dict:
    return {
        "Authorization": f"Bearer {config.GIST_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "leetcode-activity-tracker",
    }


def _fetch_gist_file_content(gist_file: dict) -> str:
    if not gist_file.get("truncated"):
        return gist_file.get("content", "") or ""

    raw_url = gist_file.get("raw_url")
    if not raw_url:
        return gist_file.get("content", "") or ""

    response = requests.get(
        raw_url,
        headers={"Authorization": f"Bearer {config.GIST_TOKEN}"},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.text


def load() -> dict:
    if not config.GIST_ID or not config.GIST_TOKEN:
        logger.warning("GIST credentials not configured. Using empty state.")
        return _default_data()

    try:
        response = requests.get(
            _gist_url(),
            headers=_gist_headers(),
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        gist = response.json()

        gist_file = gist.get("files", {}).get(GIST_FILENAME)
        if not gist_file:
            return _default_data()

        raw_content = _fetch_gist_file_content(gist_file)

    except (requests.exceptions.Timeout, requests.exceptions.RequestException, ValueError) as exc:
        logger.error("Failed to fetch gist: %s", exc)
        return _default_data()

    if not raw_content:
        return _default_data()

    try:
        data = json.loads(raw_content)
    except json.JSONDecodeError:
        logger.error("Invalid JSON stored in gist.")
        return _default_data()

    if not isinstance(data, dict):
        return _default_data()

    users = data.get("users", {})
    if not isinstance(users, dict):
        users = {}

    history = data.get("history", [])
    if not isinstance(history, list):
        history = []

    data["users"] = {
        u: _clean_user_record(r)
        for u, r in users.items()
        if isinstance(r, dict)
    }
    data["history"] = history

    return data


def save(data: dict) -> None:
    if not config.GIST_ID or not config.GIST_TOKEN:
        logger.warning("Skipping save because GIST credentials are missing.")
        return

    payload = {
        "files": {
            GIST_FILENAME: {
                "content": json.dumps(data, indent=2, ensure_ascii=False)
            }
        }
    }

    try:
        response = requests.patch(
            _gist_url(),
            headers=_gist_headers(),
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        logger.debug("Successfully updated GitHub Gist '%s'.", GIST_FILENAME)

    except (requests.exceptions.Timeout, requests.exceptions.RequestException) as exc:
        logger.error("Failed to update GitHub Gist: %s", exc)


def get_user(data: dict, username: str) -> dict:
    if username not in data["users"]:
        data["users"][username] = _empty_user_record()
    return data["users"][username]


def set_last_submission_ts(data: dict, username: str, ts: int) -> None:
    get_user(data, username)["last_submission_ts"] = ts


def get_last_submission_ts(data: dict, username: str) -> int:
    return get_user(data, username).get("last_submission_ts", 0)


def increment_daily_solves(data: dict, username: str) -> int:
    today = date.today().isoformat()
    user = get_user(data, username)
    daily = user.setdefault("daily_solves", {})
    daily[today] = daily.get(today, 0) + 1
    return daily[today]


def get_daily_solves(data: dict, username: str, day: str | None = None) -> int:
    day = day or date.today().isoformat()
    return get_user(data, username).get("daily_solves", {}).get(day, 0)


def record_history(data: dict, usernames: list[str]) -> None:
    today = date.today().isoformat()
    solves = {u: get_daily_solves(data, u) for u in usernames}

    for entry in data["history"]:
        if entry.get("date") == today:
            entry["solves"] = solves
            return

    data["history"].append(
        {
            "date": today,
            "solves": solves,
        }
    )

    data["history"] = data["history"][-90:]
