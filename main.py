"""
main.py - Entry point for the LeetCode Competition Tracker.

Usage:
    python main.py              # Run normal competition check
    python main.py leaderboard  # Send daily leaderboard to Telegram
"""

import logging
import sys

from backend import config
from backend import messages
from backend import notifier
from backend import storage
from backend import tracker

# ── Configure logging before any other imports ────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


def run_leaderboard() -> None:
    """Load state and push the daily leaderboard to Telegram."""
    data = storage.load()
    msg  = messages.generate_leaderboard_message(
        data=data,
        my_username=config.MY_USERNAME,
        opponent_usernames=config.OPPONENT_USERNAMES,
    )
    logger.info("Sending leaderboard:\n%s", msg)
    notifier.send_leaderboard(msg)


def main() -> None:
    # Validate secrets before doing anything network-related
    try:
        config.validate()
    except EnvironmentError as exc:
        logger.critical("Configuration error: %s", exc)
        sys.exit(1)

    # Route sub-commands
    if len(sys.argv) > 1 and sys.argv[1] == "leaderboard":
        run_leaderboard()
    else:
        tracker.run_check_cycle()


if __name__ == "__main__":
    main()
