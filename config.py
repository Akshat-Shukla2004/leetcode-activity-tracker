"""
config.py - Central configuration for the LeetCode Competition Tracker.
All secrets are loaded from environment variables. Never hardcode credentials.
"""

import os

# ─── Telegram ────────────────────────────────────────────────────────────────
BOT_TOKEN: str = os.environ.get("BOT_TOKEN", "")
CHAT_ID: str   = os.environ.get("CHAT_ID", "")

# ─── LeetCode Usernames ───────────────────────────────────────────────────────
_DEFAULT_MY_USERNAME = "AkshatPrep"
_DEFAULT_OPPONENT_USERNAMES = [
    "riceeater21",
    "Adarsh200IQ",
    "AbhishekSNair",
    "Akhilesh_M_2204",
    "trigun_2005",
    "shreekar6362",
    "onShoreApple",
    "devansh_shukla15",
    "ullasm07",
    "anga205",
    "shakirth-anisha",
    "aman-khandelwal",
    "Akshat18Shukla2004",
    "abhay14505",
    "sshivamanand",
    "shardool_pandey",
]

MY_USERNAME = os.environ.get("MY_USERNAME", "").strip() or _DEFAULT_MY_USERNAME

_opponents_env = os.environ.get("OPPONENT_USERNAMES", "").strip()
if _opponents_env:
    OPPONENT_USERNAMES = [u.strip() for u in _opponents_env.split(",") if u.strip()]
else:
    OPPONENT_USERNAMES = _DEFAULT_OPPONENT_USERNAMES

# ─── Storage ──────────────────────────────────────────────────────────────────
DATA_FILE: str = "data.json"

# ─── Thresholds ───────────────────────────────────────────────────────────────
# Minutes of user inactivity before messages escalate in aggression
INACTIVITY_ESCALATION_MINUTES: int = 30

# Ignore opponent submissions older than this (prevents old/baseline spam)
MAX_ALERT_AGE_HOURS: int = 24

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
