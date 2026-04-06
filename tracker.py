"""
tracker.py - Core event detection and orchestration logic.

Responsible for:
  - Checking each opponent for new accepted submissions
  - Detecting new submissions (event-based, not count-based)
  - Updating storage state
  - Triggering notifications
  - Tracking user inactivity
"""

import logging
import time
from datetime import date

import config
import leetcode
import messages
import notifier
import storage

logger = logging.getLogger(__name__)


def _get_user_inactive_minutes(data: dict) -> int:
    """
    Estimate how many minutes the user (me) has been inactive.
    Uses the last_submission_ts from storage for MY_USERNAME.
    """
    last_ts = storage.get_last_submission_ts(data, config.MY_USERNAME)
    if last_ts == 0:
        return 0  # No baseline yet — don't penalise
    return leetcode.minutes_ago(last_ts)


def check_opponent(data: dict, opponent: str) -> bool:
    """
    Check a single opponent for new submissions.

    Algorithm:
      1. Fetch latest accepted submission from LeetCode
      2. Compare its timestamp against last-seen in storage
      3. If newer → new event → alert + update state
      4. If same or older → no-op

    Args:
        data:     Loaded storage dict (mutated in place).
        opponent: Opponent's LeetCode username.

    Returns:
        True if a new submission was detected and acted upon, else False.
    """
    latest = leetcode.get_latest_accepted(opponent)

    if not latest:
        logger.info("No accepted submissions found for '%s'.", opponent)
        return False

    new_ts   = latest["timestamp"]
    last_ts  = storage.get_last_submission_ts(data, opponent)

    # Guard: already seen this exact submission (or something newer)
    if new_ts <= last_ts:
        logger.info(
            "'%s' — no new submission (latest ts=%d, last seen=%d).",
            opponent, new_ts, last_ts,
        )
        return False

    # ── NEW SUBMISSION DETECTED ───────────────────────────────────────────────
    problem = latest["title"]
    logger.info(
        "NEW submission for '%s': '%s' at ts=%d", opponent, problem, new_ts
    )

    # Guard: don't alert on very old solves (e.g., first run after reset)
    max_age_seconds = int(config.MAX_ALERT_AGE_HOURS * 60 * 60)
    age_seconds = leetcode.seconds_ago(new_ts)
    if age_seconds > max_age_seconds:
        logger.info(
            "'%s' latest accepted is %.1f hours old (cutoff=%d hours) — syncing baseline only.",
            opponent,
            age_seconds / 3600,
            config.MAX_ALERT_AGE_HOURS,
        )
        storage.set_last_submission_ts(data, opponent, new_ts)
        return False

    # Update storage first to prevent double-alerts even if notify fails
    storage.set_last_submission_ts(data, opponent, new_ts)
    daily_count = storage.increment_daily_solves(data, opponent)
    streak      = storage.update_streak(data, opponent)

    logger.info(
        "'%s' daily count: %d | streak: %d", opponent, daily_count, streak
    )

    # Build and send the alert
    user_inactive = _get_user_inactive_minutes(data)
    msg = messages.generate_alert_message(
        opponent=opponent,
        problem=problem,
        submission_ts=new_ts,
        user_inactive_minutes=user_inactive,
        opponent_streak=streak,
    )

    success = notifier.send_alert(msg)
    if not success:
        logger.warning("Alert for '%s' failed to send.", opponent)

    return True


def check_user_inactivity(data: dict) -> None:
    """
    If the user has been inactive for longer than the escalation threshold,
    send a silent nudge. This runs regardless of opponent activity.
    """
    inactive_min = _get_user_inactive_minutes(data)

    # Only nudge if we have a baseline AND threshold exceeded
    last_ts = storage.get_last_submission_ts(data, config.MY_USERNAME)
    if last_ts == 0:
        return

    if inactive_min >= config.INACTIVITY_ESCALATION_MINUTES:
        logger.info(
            "User inactive for %d min — sending nudge.", inactive_min
        )
        nudge = messages.generate_inactivity_nudge(inactive_min)
        notifier.send_silent(nudge)


def sync_my_activity(data: dict) -> None:
    """
    Fetch my own latest submission and update storage.
    Used to keep the inactivity tracker honest.
    """
    latest = leetcode.get_latest_accepted(config.MY_USERNAME)
    if not latest:
        return

    new_ts  = latest["timestamp"]
    last_ts = storage.get_last_submission_ts(data, config.MY_USERNAME)

    if new_ts > last_ts:
        logger.info(
            "My new submission: '%s' at ts=%d", latest["title"], new_ts
        )
        storage.set_last_submission_ts(data, config.MY_USERNAME, new_ts)
        storage.increment_daily_solves(data, config.MY_USERNAME)
        storage.update_streak(data, config.MY_USERNAME)


def run_check_cycle() -> None:
    """
    Full check cycle — called by main.py on every GitHub Actions run.

    Steps:
      1. Load persisted state
      2. Sync my own activity
      3. Check each opponent for new submissions
      4. Optionally nudge if I've been inactive
      5. Record history snapshot
      6. Persist updated state
    """
    logger.info("─── Starting check cycle ───")
    data = storage.load()

    # Sync my own latest solve (for inactivity tracking)
    sync_my_activity(data)

    # Check all configured opponents
    new_events = 0
    for opponent in config.OPPONENT_USERNAMES:
        try:
            found = check_opponent(data, opponent)
            if found:
                new_events += 1
        except Exception as exc:
            # Never crash the whole run due to one opponent failing
            logger.exception("Unexpected error checking '%s': %s", opponent, exc)

    logger.info("Check cycle complete. New events: %d", new_events)

    # Inactivity nudge (only if no new events to avoid double-notifying)
    if new_events == 0:
        try:
            check_user_inactivity(data)
        except Exception as exc:
            logger.exception("Inactivity check failed: %s", exc)

    # Snapshot history for graph data
    all_users = [config.MY_USERNAME] + config.OPPONENT_USERNAMES
    storage.record_history(data, all_users)

    # Persist all updates atomically
    storage.save(data)
    logger.info("─── Check cycle saved ───")
