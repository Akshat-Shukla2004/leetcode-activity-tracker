import time

from backend import messages


def test_escape_telegram_markdown():
    text = "_hello_*world*`code`[link]"
    escaped = messages._escape_telegram_markdown(text)

    assert "\\_" in escaped
    assert "\\*" in escaped
    assert "\\`" in escaped
    assert "\\[" in escaped


def test_format_handles_missing_keys():
    result = messages._format(
        "Hello {name} {missing}",
        name="Akshat",
    )

    assert result == "Hello {name} {missing}"


def test_generate_alert_message():
    msg = messages.generate_alert_message(
        opponent="john",
        problem="Two Sum",
        submission_ts=int(time.time()) - 60,
        user_inactive_minutes=20,
        opponent_streak=4,
    )

    assert isinstance(msg, str)
    assert len(msg) > 0
    assert "john" in msg
    assert "Two Sum" in msg


def test_generate_leaderboard_message():
    today = messages.date.today().isoformat()

    data = {
        "users": {
            "me": {
                "daily_solves": {
                    today: 3,
                },
                "streak": 2,
            },
            "alice": {
                "daily_solves": {
                    today: 5,
                },
                "streak": 6,
            },
            "bob": {
                "daily_solves": {
                    today: 1,
                },
                "streak": 0,
            },
        },
        "history": [],
    }

    leaderboard = messages.generate_leaderboard_message(
        data,
        "me",
        ["alice", "bob"],
    )

    assert "Daily Leaderboard" in leaderboard
    assert "alice" in leaderboard
    assert "bob" in leaderboard
    assert "You" in leaderboard
    assert "Opponents solved" in leaderboard


def test_generate_inactivity_nudge():
    msg = messages.generate_inactivity_nudge(45)

    assert isinstance(msg, str)
    assert "45" in msg


def test_generate_alert_escapes_markdown():
    msg = messages.generate_alert_message(
        opponent="john_doe",
        problem="Binary*Tree",
        submission_ts=int(time.time()) - 60,
    )

    # Opponent name always appears in every template
    assert "john\\_doe" in msg

def test_leaderboard_is_sorted():
    today = messages.date.today().isoformat()

    data = {
        "users": {
            "me": {
                "daily_solves": {today: 1},
                "streak": 0,
            },
            "alice": {
                "daily_solves": {today: 5},
                "streak": 0,
            },
            "bob": {
                "daily_solves": {today: 3},
                "streak": 0,
            },
        },
        "history": [],
    }

    leaderboard = messages.generate_leaderboard_message(
        data,
        "me",
        ["alice", "bob"],
    )

    assert leaderboard.find("alice") < leaderboard.find("bob")
    assert leaderboard.find("bob") < leaderboard.find("You")