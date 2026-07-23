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

from backend import config
from backend import leetcode
from backend import messages
from backend import notifier
from backend import storage

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


def check_opponent(data: dict, opponent: str) -> int:
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
        Number of new submissions detected and acted upon.
    """
    last_ts = storage.get_last_submission_ts(data, opponent)

    # First time seeing this opponent: set baseline only, no retroactive alert.
    if last_ts == 0:
        latest = leetcode.get_latest_accepted(opponent)

        if not latest:
            logger.info("No accepted submissions found for '%s'.", opponent)
            return 0

        new_ts = latest["timestamp"]
        logger.info(
            "'%s' baseline initialized at ts=%d (no alert on first sync).",
            opponent,
            new_ts,
        )
        storage.set_last_submission_ts(data, opponent, new_ts)
        return 0

    submissions = leetcode.get_accepted_submissions_since(opponent, since_ts=last_ts)

    if not submissions:
        logger.info("No accepted submissions found for '%s'.", opponent)
        return 0

    # Guard: don't alert on very old solves (e.g., first run after reset)
    max_age_seconds = int(config.MAX_ALERT_AGE_HOURS * 60 * 60)
    fresh_submissions = [
        submission
        for submission in submissions
        if leetcode.seconds_ago(submission["timestamp"]) <= max_age_seconds
    ]

    if not fresh_submissions:
        newest_ts = submissions[-1]["timestamp"]
        logger.info(
            "'%s' latest accepted is too old (cutoff=%d hours) — syncing baseline to ts=%d.",
            opponent,
            config.MAX_ALERT_AGE_HOURS,
            newest_ts,
        )
        storage.set_last_submission_ts(data, opponent, newest_ts)
        return 0

    alert_count = 0
    last_seen_ts = last_ts
    user_record = data["users"][opponent]
    processed = set(user_record.get("processed_submissions", []))

    for submission in fresh_submissions:
        new_ts = submission["timestamp"]
        if new_ts in processed:
            logger.info(
                "Skipping duplicate submission for '%s' at ts=%d",
                opponent,
                new_ts,
            )
            continue
        problem = submission["title"]
        logger.info("NEW submission for '%s': '%s' at ts=%d", opponent, problem, new_ts)

        daily_count = storage.increment_daily_solves(data, opponent)

        logger.info("'%s' daily count: %d", opponent, daily_count)

        problem_slug = submission.get("titleSlug", "")
        problem_difficulty = ""
        if problem_slug:
            details = leetcode.get_question_details(problem_slug)
            if details:
                problem_difficulty = details.get("difficulty", "")

        user_inactive = _get_user_inactive_minutes(data)
        msg = messages.generate_alert_message(
            opponent=opponent,
            problem=problem,
            submission_ts=new_ts,
            problem_slug=problem_slug,
            problem_difficulty=problem_difficulty,
            user_inactive_minutes=user_inactive,
        )

        success = notifier.send_alert(msg)

        if success:
            storage.set_last_submission_ts(data, opponent, new_ts)
            last_seen_ts = new_ts
            alert_count += 1
        else:
            logger.warning("Alert for '%s' failed to send.", opponent)

    return alert_count


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
        logger.info("User inactive for %d min — sending nudge.", inactive_min)
        nudge = messages.generate_inactivity_nudge(inactive_min)
        notifier.send_silent(nudge)


def sync_my_activity(data: dict) -> None:
    """
    Fetch my own latest submission and update storage.
    Used to keep the inactivity tracker honest.
    """
    last_ts = storage.get_last_submission_ts(data, config.MY_USERNAME)

    if last_ts == 0:
        latest = leetcode.get_latest_accepted(config.MY_USERNAME)
        if not latest:
            return

        new_ts = latest["timestamp"]
        logger.info(
            "Initialized my baseline at ts=%d (no retroactive self-count).", new_ts
        )
        storage.set_last_submission_ts(data, config.MY_USERNAME, new_ts)
        return

    submissions = leetcode.get_accepted_submissions_since(
        config.MY_USERNAME,
        since_ts=last_ts,
    )

    if not submissions:
        return

    for submission in submissions:
        new_ts = submission["timestamp"]
        logger.info("My new submission: '%s' at ts=%d", submission["title"], new_ts)
        storage.set_last_submission_ts(data, config.MY_USERNAME, new_ts)
        storage.increment_daily_solves(data, config.MY_USERNAME)


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
            new_events += check_opponent(data, opponent)
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

    logger.info(
        "Persisting daily_solves snapshot before save: %s",
        {
            username: record.get("daily_solves", {})
            for username, record in data.get("users", {}).items()
        },
    )

    # Persist all updates atomically
    storage.save(data)
    logger.info("─── Check cycle saved ───")
