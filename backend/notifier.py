"""notifier.py - Telegram notification layer.

This module is intentionally small and depends only on `requests`.
"""

from __future__ import annotations

import logging
from typing import Any

import requests

from backend import config

logger = logging.getLogger(__name__)


def _telegram_api_url(method: str) -> str:
    return f"https://api.telegram.org/bot{config.BOT_TOKEN}/{method}"


def _send_raw(text: str, *, disable_notification: bool) -> bool:
    """Send a single Telegram message. Returns True on success."""
    url = _telegram_api_url("sendMessage")
    payload: dict[str, Any] = {
        "chat_id": config.CHAT_ID,
        "text": text,
        "disable_notification": disable_notification,
        "disable_web_page_preview": True,
        "parse_mode": "Markdown",
    }

    try:
        resp = requests.post(url, json=payload, timeout=20)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as exc:
        logger.error("Telegram sendMessage request failed: %s", exc)
        return False
    except ValueError as exc:
        logger.error("Telegram sendMessage returned non-JSON: %s", exc)
        return False

    if not isinstance(data, dict) or not data.get("ok"):
        logger.error("Telegram sendMessage failed: %s", data)
        return False

    return True


def send_alert(body: str) -> bool:
    """Send a single alert message with a normal Telegram notification."""

    return _send_raw(body, disable_notification=False)


def send_silent(body: str) -> bool:
    """Send a single silent message (no push notification)."""
    return _send_raw(body, disable_notification=True)


def send_leaderboard(body: str) -> bool:
    """Send a normal leaderboard message (with notification)."""
    return _send_raw(body, disable_notification=False)
