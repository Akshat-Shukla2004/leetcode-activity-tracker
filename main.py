"""
main.py - Entry point for the LeetCode Competition Tracker.

Usage:
    python main.py              # Run normal competition check
    python main.py leaderboard  # Send daily leaderboard to Telegram
"""

import logging
import sys

from backend import config
from backend import tracker

# ── Configure logging before any other imports ────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)



def main() -> None:
    # Validate secrets before doing anything network-related
    try:
        config.validate()
    except EnvironmentError as exc:
        logger.critical("Configuration error: %s", exc)
        sys.exit(1)
    tracker.run_check_cycle()


if __name__ == "__main__":
    main()
