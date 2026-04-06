"""notifier.py - Telegram notification layer.

Implements the "two-message" stealth alert pattern:
  1) A short bait message (notifies)
  2) The real message (silent)

This module is intentionally small and depends only on `requests`.
"""

from __future__ import annotations

import logging
import random
import time
from typing import Any

import requests

import config

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
    """Send the two-part stealth alert (bait + silent body)."""

    fake_msgs = [
        "hop on fort",
        "bro come valo?",
        "1 game?",
        "queue?",
        "u online?",
        "come discord",
        "quick match?",
        "we need 1 more",
        "join fast",
        "playing?",
    ]

    bait = random.choice(fake_msgs)

    ok1 = _send_raw(bait, disable_notification=False)
    if not ok1:
        logger.error("Failed to send bait message; skipping body.")
        return False

    # Small delay so messages arrive in order
    time.sleep(0.7)

    ok2 = _send_raw(body, disable_notification=True)
    return ok1 and ok2


def send_silent(body: str) -> bool:
    """Send a single silent message (no push notification)."""
    return _send_raw(body, disable_notification=True)


def send_leaderboard(body: str) -> bool:
    """Send a normal leaderboard message (with notification)."""
    return _send_raw(body, disable_notification=False)