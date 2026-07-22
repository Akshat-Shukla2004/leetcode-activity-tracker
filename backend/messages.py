"""
messages.py - Dynamic, psychologically engaging message engine.

Messages are grouped into categories and selected randomly.
Intensity scales based on how long the user has been inactive.
"""

import random
import time

from backend import config


# ─── Message templates ────────────────────────────────────────────────────────
# Use {problem}, {minutes}, {opponent}, {user_inactive} as placeholders.

_AGGRESSIVE = [
    "😈 {opponent} just solved *{problem}* — {minutes} min ago. You did nothing.",
    "🔥 {opponent} is grinding *{problem}*. You're watching.",
    "💀 {opponent} solved *{problem}* {minutes} minutes ago. Still comfortable?",
    "😤 Another one. *{problem}* down for {opponent}. You haven't moved.",
    "⚔️ {opponent} just clocked *{problem}*. Your turn — or are you scared?",
    "😂 {minutes} minutes ago {opponent} solved *{problem}*. What's your excuse?",
]

_SMART_PRESSURE = [
    "🧠 {opponent} solved *{problem}* recently. You've been inactive for {user_inactive} min.",
    "📊 {opponent} is building momentum. *{problem}* solved {minutes} min ago. You're falling behind.",
    "🎯 Consistent effort wins. {opponent} knows that — *{problem}* done {minutes} min ago.",
    "🧩 *{problem}* checked off by {opponent}. The gap is growing silently.",
    "📈 {opponent} solved *{problem}* {minutes} min ago. Every minute you wait, the lead widens.",
]

_TIME_URGENCY = [
    "⏳ {minutes} minutes ago {opponent} moved ahead with *{problem}*. Clock's ticking.",
    "⌛ {minutes} min. That's how long ago {opponent} solved *{problem}* and you still haven't started.",
    "🚨 *{problem}* — {opponent} solved it {minutes} minutes ago. Time is the only thing you can't get back.",
    "⏰ {minutes} minutes of inactivity. {opponent} didn't waste those minutes.",
]

_NUCLEAR = [
    "☢️ WAKE UP. {opponent} solved *{problem}* {minutes} min ago AND you've been idle for {user_inactive} min. This is embarrassing.",
    "🔴 RED ALERT. {user_inactive} min of silence from you. {opponent} just solved *{problem}*. {opponent} is not stopping.",
    "😡 {user_inactive} minutes. That's how long you've done nothing while {opponent} solved *{problem}*. Unacceptable.",
]


def _format(template: str, **kwargs) -> str:
    """Safely format a template, ignoring unknown placeholders."""
    try:
        return template.format(**kwargs)
    except KeyError:
        return template


def _escape_telegram_markdown(text: str) -> str:
    """Escape characters that can break Telegram's legacy Markdown parse mode."""
    # Escape backslash first to avoid double-escaping.
    text = text.replace("\\", "\\\\")
    for ch in ("_", "*", "`", "["):
        text = text.replace(ch, f"\\{ch}")
    return text


def generate_alert_message(
    opponent: str,
    problem: str,
    submission_ts: int,
    problem_slug: str = "",
    problem_difficulty: str = "",
    user_inactive_minutes: int = 0,
) -> str:
    """
    Generate a dynamic alert message for a new opponent submission.

    Args:
        opponent:               Opponent's username.
        problem:                Problem title they solved.
        submission_ts:          Unix timestamp of their submission.
        problem_slug:           LeetCode slug for the solved problem.
        problem_difficulty:     Optional problem difficulty if available.
        user_inactive_minutes:  How many minutes the user has been inactive.

    Returns:
        Formatted Telegram-ready markdown string.
    """
    minutes = max(0, int((time.time() - submission_ts) / 60))

    kwargs = {
        "opponent": _escape_telegram_markdown(opponent),
        "problem": _escape_telegram_markdown(problem),
        "minutes": minutes,
        "user_inactive": user_inactive_minutes,
    }

    # Escalate intensity based on user inactivity
    if user_inactive_minutes >= config.INACTIVITY_ESCALATION_MINUTES:
        pool = _NUCLEAR + _AGGRESSIVE
    elif user_inactive_minutes >= 15:
        pool = _AGGRESSIVE + _TIME_URGENCY
    else:
        pool = _AGGRESSIVE + _SMART_PRESSURE + _TIME_URGENCY

    template = random.choice(pool)
    body = _format(template, **kwargs)

    details = [f"*Problem:* {_escape_telegram_markdown(problem)}"]
    if problem_difficulty:
        details.append(f"*Difficulty:* {_escape_telegram_markdown(problem_difficulty)}")

    if problem_slug:
        problem_url = f"https://leetcode.com/problems/{problem_slug}/"
        details.append(f"*URL:* {problem_url}")

    return body + "\n\n" + "\n".join(details)


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
