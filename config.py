"""
config.py - Central configuration for the LeetCode Competition Tracker.
All secrets are loaded from environment variables. Never hardcode credentials.
"""

import os

# ─── Telegram ────────────────────────────────────────────────────────────────
BOT_TOKEN: str = os.environ.get("BOT_TOKEN", "")
CHAT_ID: str   = os.environ.get("CHAT_ID", "")

# ─── LeetCode Usernames ───────────────────────────────────────────────────────
MY_USERNAME: str = os.environ.get("MY_USERNAME", "your_username")

# Support multiple opponents as a comma-separated env var, e.g. "alice,bob"
_raw_opponents = os.environ.get("OPPONENT_USERNAMES", "opponent_username")
OPPONENT_USERNAMES: list[str] = [u.strip() for u in _raw_opponents.split(",") if u.strip()]

# ─── Storage ──────────────────────────────────────────────────────────────────
DATA_FILE: str = "data.json"

# ─── Thresholds ───────────────────────────────────────────────────────────────
# Minutes of user inactivity before messages escalate in aggression
INACTIVITY_ESCALATION_MINUTES: int = 30

# ─── Validation ───────────────────────────────────────────────────────────────
def validate() -> None:
    """Raise early if required secrets are missing."""
    missing = []
    if not BOT_TOKEN:
        missing.append("BOT_TOKEN")
    if not CHAT_ID:
        missing.append("CHAT_ID")
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}"
        )
