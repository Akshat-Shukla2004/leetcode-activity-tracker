from datetime import date, timedelta

from backend import storage


def test_load_returns_default_when_file_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(storage.config, "DATA_FILE", str(tmp_path / "missing.json"))

    data = storage.load()

    assert data == {
        "users": {},
        "history": [],
    }


def test_get_user_auto_creates_user():
    data = {
        "users": {},
        "history": [],
    }

    user = storage.get_user(data, "akshat")

    assert "akshat" in data["users"]
    assert user["last_submission_ts"] == 0
    assert user["streak"] == 0
    assert user["daily_solves"] == {}


def test_set_and_get_last_submission():
    data = {
        "users": {},
        "history": [],
    }

    storage.set_last_submission_ts(data, "akshat", 12345)

    assert storage.get_last_submission_ts(data, "akshat") == 12345


def test_increment_daily_solves():
    data = {
        "users": {},
        "history": [],
    }

    count1 = storage.increment_daily_solves(data, "akshat")
    count2 = storage.increment_daily_solves(data, "akshat")

    assert count1 == 1
    assert count2 == 2

    today = date.today().isoformat()

    assert (
        data["users"]["akshat"]["daily_solves"][today]
        == 2
    )


def test_get_daily_solves():
    data = {
        "users": {},
        "history": [],
    }

    today = date.today().isoformat()

    storage.get_user(data, "akshat")["daily_solves"][today] = 7

    assert storage.get_daily_solves(data, "akshat") == 7


def test_update_streak_first_day():
    data = {
        "users": {},
        "history": [],
    }

    streak = storage.update_streak(data, "akshat")

    assert streak == 1


def test_update_streak_consecutive_days():
    yesterday = (date.today() - timedelta(days=1)).isoformat()

    data = {
        "users": {
            "akshat": {
                "last_submission_ts": 0,
                "streak": 5,
                "last_solve_date": yesterday,
                "daily_solves": {},
            }
        },
        "history": [],
    }

    streak = storage.update_streak(data, "akshat")

    assert streak == 6


def test_record_history():
    today = date.today().isoformat()

    data = {
        "users": {
            "akshat": {
                "last_submission_ts": 0,
                "streak": 0,
                "last_solve_date": "",
                "daily_solves": {
                    today: 3,
                },
            }
        },
        "history": [],
    }

    storage.record_history(data, ["akshat"])

    assert len(data["history"]) == 1
    assert data["history"][0]["date"] == today
    assert data["history"][0]["solves"]["akshat"] == 3