"""
notifier.py - Telegram Bot notification system.

Strategy: two-message pattern
  1. First message: "⚠️ Alert" — triggers a push notification preview
     (preview shows nothing useful)
  2. Second message: silent (no notification) — contains the actual details
     (user must open the app to read it)

This hides the content from the notification preview, adding psychological tension.
"""

import logging
import time
import requests

import config

logger = logging.getLogger(__name__)

TELEGRAM_API_BASE = "https://api.telegram.org/bot{token}/{method}"


def _api_url(method: str) -> str:
    return TELEGRAM_API_BASE.format(token=config.BOT_TOKEN, method=method)


def _send_raw(
    text: str,
    disable_notification: bool = False,
    parse_mode: str = "Markdown",
    retries: int = 3,
) -> bool:
    """
    Low-level wrapper around Telegram's sendMessage.

    Args:
        text:                 Message body.
        disable_notification: If True, message arrives silently.
        parse_mode:           "Markdown" or "HTML".
        retries:              Number of retry attempts on failure.

    Returns:
        True on success, False on all failures.
    """
    payload = {
        "chat_id":              config.CHAT_ID,
        "text":                 text,
        "parse_mode":           parse_mode,
        "disable_notification": disable_notification,
    }

    for attempt in range(1, retries + 1):
        try:
            resp = requests.post(
                _api_url("sendMessage"),
                json=payload,
                timeout=10,
            )
            resp.raise_for_status()
            result = resp.json()

            if result.get("ok"):
                logger.debug("Telegram message sent (silent=%s)", disable_notification)
                return True
            else:
                logger.error(
                    "Telegram API returned not-ok: %s", result.get("description")
                )
                return False

        except requests.exceptions.Timeout:
            logger.warning("Telegram request timed out (attempt %d/%d)", attempt, retries)
        except requests.exceptions.RequestException as exc:
            logger.error("Telegram request failed (attempt %d/%d): %s", attempt, retries, exc)

        if attempt < retries:
            time.sleep(2 ** attempt)  # Exponential back-off: 2s, 4s

    logger.error("All %d Telegram send attempts failed.", retries)
    return False


def send_alert(body: str) -> bool:
    """
    Send a two-part alert:
      Part 1 → "⚠️ Alert"      (WITH notification — preview shows only this)
      Part 2 → actual message   (SILENT — hidden until app is opened)

    Returns True if both messages were sent successfully.
    """
    ok1 = _send_raw("⚠️ Alert", disable_notification=False)
    if not ok1:
        logger.error("Failed to send alert header; skipping body.")
        return False

    # Small delay so messages arrive in correct order
    time.sleep(0.5)

    ok2 = _send_raw(body, disable_notification=True)
    return ok1 and ok2


def send_silent(body: str) -> bool:
    """Send a single silent message (no push notification)."""
    return _send_raw(body, disable_notification=True)


def send_leaderboard(body: str) -> bool:
    """Send the daily leaderboard as a silent message."""
    return send_silent(body)
