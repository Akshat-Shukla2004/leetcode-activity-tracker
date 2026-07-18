from datetime import date

from backend import storage


def test_load_returns_default_when_file_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(storage.config, "DATA_FILE", str(tmp_path / "missing.json"))

    data = storage.load()

    assert data == {
        "users": {},
        "history": [],
    }


def test_load_returns_default_when_file_corrupted(monkeypatch, tmp_path):
    data_file = tmp_path / "corrupted.json"
    data_file.write_text("{not valid json", encoding="utf-8")

    monkeypatch.setattr(storage.config, "DATA_FILE", str(data_file))

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
    assert user == {
        "last_submission_ts": 0,
        "daily_solves": {},
    }


def test_get_user_can_add_multiple_users():
    data = {
        "users": {},
        "history": [],
    }

    storage.get_user(data, "akshat")
    storage.get_user(data, "alice")

    assert set(data["users"].keys()) == {"akshat", "alice"}


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

    assert data["users"]["akshat"]["daily_solves"][today] == 2


def test_get_daily_solves():
    data = {
        "users": {},
        "history": [],
    }

    today = date.today().isoformat()

    storage.get_user(data, "akshat")["daily_solves"][today] = 7

    assert storage.get_daily_solves(data, "akshat") == 7


def test_record_history():
    today = date.today().isoformat()

    data = {
        "users": {
            "akshat": {
                "last_submission_ts": 0,
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


def test_save_and_load_cycle(monkeypatch, tmp_path):
    data_file = tmp_path / "data.json"
    monkeypatch.setattr(storage.config, "DATA_FILE", str(data_file))

    today = date.today().isoformat()
    original = {
        "users": {
            "akshat": {
                "last_submission_ts": 123,
                "daily_solves": {today: 2},
            },
            "alice": {
                "last_submission_ts": 456,
                "daily_solves": {today: 5},
            },
        },
        "history": [
            {"date": today, "solves": {"akshat": 2, "alice": 5}},
        ],
    }

    storage.save(original)
    loaded = storage.load()

    assert loaded == original


def test_load_strips_legacy_streak_fields(monkeypatch, tmp_path):
    data_file = tmp_path / "legacy.json"
    data_file.write_text(
        """
        {
          "users": {
            "akshat": {
              "last_submission_ts": 123,
              "streak": 9,
              "last_solve_date": "2026-07-16",
              "daily_solves": {"2026-07-17": 3}
            }
          },
          "history": []
        }
        """,
        encoding="utf-8",
    )

    monkeypatch.setattr(storage.config, "DATA_FILE", str(data_file))

    loaded = storage.load()

    assert loaded == {
        "users": {
            "akshat": {
                "last_submission_ts": 123,
                "daily_solves": {"2026-07-17": 3},
            }
        },
        "history": [],
    }
