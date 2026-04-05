"""
messages.py - Dynamic, psychologically engaging message engine.

Messages are grouped into categories and selected randomly.
Intensity scales based on how long the user has been inactive.
"""

import random
import time
from datetime import date

import config


# ─── Message templates ────────────────────────────────────────────────────────
# Use {problem}, {minutes}, {opponent}, {streak} as placeholders.

_AGGRESSIVE = [
    "😈 {opponent} just solved *{problem}* — {minutes} min ago. You did nothing.",
    "🔥 He's grinding *{problem}*. You're watching.",
    "💀 {opponent} solved *{problem}* {minutes} minutes ago. Still comfortable?",
    "😤 Another one. *{problem}* down for {opponent}. You haven't moved.",
    "⚔️ {opponent} just clocked *{problem}*. Your turn — or are you scared?",
    "😂 {minutes} minutes ago he solved *{problem}*. What's your excuse?",
]

_SMART_PRESSURE = [
    "🧠 {opponent} solved *{problem}* recently. You've been inactive for {user_inactive} min.",
    "📊 He's building momentum. *{problem}* solved {minutes} min ago. You're falling behind.",
    "🎯 Consistent effort wins. {opponent} knows that — *{problem}* done {minutes} min ago.",
    "🧩 *{problem}* checked off by {opponent}. The gap is growing silently.",
    "📈 {opponent} solved *{problem}* {minutes} min ago. Every minute you wait, the lead widens.",
]

_TIME_URGENCY = [
    "⏳ {minutes} minutes ago he moved ahead with *{problem}*. Clock's ticking.",
    "⌛ {minutes} min. That's how long ago {opponent} solved *{problem}* and you still haven't started.",
    "🚨 *{problem}* — solved {minutes} minutes ago. Time is the only thing you can't get back.",
    "⏰ {minutes} minutes of inactivity. {opponent} didn't waste his.",
]

_NUCLEAR = [
    "☢️ WAKE UP. {opponent} solved *{problem}* {minutes} min ago AND you've been idle for {user_inactive} min. This is embarrassing.",
    "🔴 RED ALERT. {user_inactive} min of silence from you. {opponent} just solved *{problem}*. He's not stopping.",
    "💣 {opponent} is on a {streak}-day streak and just solved *{problem}*. You're coasting. Stop it.",
    "😡 {user_inactive} minutes. That's how long you've done nothing while {opponent} solved *{problem}*. Unacceptable.",
]

_STREAK_CALLOUT = [
    "🔥 {opponent} is on a {streak}-day streak. Just solved *{problem}*. Do you even have a streak?",
    "📅 Day {streak} of {opponent}'s streak — *{problem}* just checked off. What day is your streak on?",
    "💪 {streak} days in a row for {opponent}. Today: *{problem}*. Consistency beats talent.",
]


def _format(template: str, **kwargs) -> str:
    """Safely format a template, ignoring unknown placeholders."""
    try:
        return template.format(**kwargs)
    except KeyError:
        return template


def generate_alert_message(
    opponent: str,
    problem: str,
    submission_ts: int,
    user_inactive_minutes: int = 0,
    opponent_streak: int = 0,
) -> str:
    """
    Generate a dynamic alert message for a new opponent submission.

    Args:
        opponent:               Opponent's username.
        problem:                Problem title they solved.
        submission_ts:          Unix timestamp of their submission.
        user_inactive_minutes:  How many minutes the user has been inactive.
        opponent_streak:        Opponent's current streak.

    Returns:
        Formatted Telegram-ready markdown string.
    """
    minutes = max(0, int((time.time() - submission_ts) / 60))

    kwargs = {
        "opponent":      opponent,
        "problem":       problem,
        "minutes":       minutes,
        "user_inactive": user_inactive_minutes,
        "streak":        opponent_streak,
    }

    # Escalate intensity based on user inactivity
    if user_inactive_minutes >= config.INACTIVITY_ESCALATION_MINUTES:
        # Nuclear tier — user has been very inactive
        pool = _NUCLEAR + _AGGRESSIVE
    elif opponent_streak >= 3:
        # Highlight the streak
        pool = _STREAK_CALLOUT + _SMART_PRESSURE
    elif user_inactive_minutes >= 15:
        # Moderate pressure
        pool = _AGGRESSIVE + _TIME_URGENCY
    else:
        # Standard rotation across all tiers
        pool = _AGGRESSIVE + _SMART_PRESSURE + _TIME_URGENCY

    template = random.choice(pool)
    return _format(template, **kwargs)


def generate_leaderboard_message(
    data: dict,
    my_username: str,
    opponent_usernames: list[str],
) -> str:
    """
    Generate a formatted daily leaderboard summary.

    Args:
        data:               Loaded storage data dict.
        my_username:        Your LeetCode username.
        opponent_usernames: List of opponent usernames.

    Returns:
        Telegram-ready markdown string.
    """
    from storage import get_daily_solves, get_streak

    today = date.today().isoformat()
    lines = [f"📊 *Daily Leaderboard — {today}*\n"]

    all_users = [my_username] + opponent_usernames
    entries = []
    for uname in all_users:
        solves = get_daily_solves(data, uname)
        streak = get_streak(data, uname)
        label = "🧑 You" if uname == my_username else f"😈 {uname}"
        entries.append((solves, streak, label))

    # Sort by descending solve count
    entries.sort(key=lambda e: e[0], reverse=True)

    for rank, (solves, streak, label) in enumerate(entries, start=1):
        medal = ["🥇", "🥈", "🥉"][rank - 1] if rank <= 3 else f"{rank}."
        fire  = f" 🔥×{streak}" if streak > 0 else ""
        lines.append(f"{medal} {label}: *{solves}* solve(s) today{fire}")

    return "\n".join(lines)


def generate_inactivity_nudge(user_inactive_minutes: int) -> str:
    """
    Generate a nudge message when the user themselves have been inactive too long.
    """
    templates = [
        f"🥱 You've been inactive for *{user_inactive_minutes} minutes*. Open LeetCode.",
        f"😴 {user_inactive_minutes} minutes of nothing. They're not resting.",
        f"⚡ {user_inactive_minutes}-minute drought. Fix it.",
        f"🕰️ *{user_inactive_minutes} min* idle. The leaderboard doesn't pause for you.",
    ]
    return random.choice(templates)
