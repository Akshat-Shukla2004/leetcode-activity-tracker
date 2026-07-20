from datetime import date
import json
from unittest.mock import Mock

import requests

from backend import storage


DEFAULT_DATA = {
    "users": {},
    "history": [],
}


def _default_data():
    return {
        "users": {},
        "history": [],
    }


def _gist_response(*, gist_json=None, gist_text=None, json_side_effect=None):
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.side_effect = json_side_effect
    if gist_json is not None:
        response.json.return_value = gist_json
    response.text = gist_text
    return response


def _configure_gist_credentials(monkeypatch):
    monkeypatch.setattr(storage.config, "GIST_ID", "gist-123")
    monkeypatch.setattr(storage.config, "GIST_TOKEN", "token-abc")


def test_load_returns_default_when_gist_credentials_are_missing(monkeypatch):
    monkeypatch.setattr(storage.config, "GIST_ID", "")
    monkeypatch.setattr(storage.config, "GIST_TOKEN", "")

    assert storage.load() == DEFAULT_DATA


def test_load_returns_default_when_requests_get_times_out(monkeypatch):
    _configure_gist_credentials(monkeypatch)
    get_mock = Mock(side_effect=requests.exceptions.Timeout())
    monkeypatch.setattr(storage.requests, "get", get_mock)

    assert storage.load() == DEFAULT_DATA
    get_mock.assert_called_once()


def test_load_returns_default_when_requests_get_raises_request_exception(monkeypatch):
    _configure_gist_credentials(monkeypatch)
    get_mock = Mock(side_effect=requests.exceptions.RequestException())
    monkeypatch.setattr(storage.requests, "get", get_mock)

    assert storage.load() == DEFAULT_DATA
    get_mock.assert_called_once()


def test_load_returns_default_when_gist_file_is_missing(monkeypatch):
    _configure_gist_credentials(monkeypatch)
    response = _gist_response(gist_json={"files": {}})
    get_mock = Mock(return_value=response)
    monkeypatch.setattr(storage.requests, "get", get_mock)

    assert storage.load() == DEFAULT_DATA
    get_mock.assert_called_once()


def test_load_returns_default_when_gist_file_content_is_empty(monkeypatch):
    _configure_gist_credentials(monkeypatch)
    response = _gist_response(
        gist_json={
            "files": {
                storage.GIST_FILENAME: {"content": ""}
            }
        }
    )
    get_mock = Mock(return_value=response)
    monkeypatch.setattr(storage.requests, "get", get_mock)

    assert storage.load() == DEFAULT_DATA
    get_mock.assert_called_once()


def test_load_returns_default_when_gist_json_is_invalid(monkeypatch):
    _configure_gist_credentials(monkeypatch)
    response = _gist_response(json_side_effect=ValueError("invalid json"))
    get_mock = Mock(return_value=response)
    monkeypatch.setattr(storage.requests, "get", get_mock)

    assert storage.load() == DEFAULT_DATA
    get_mock.assert_called_once()


def test_load_returns_default_when_gist_content_is_not_a_json_object(monkeypatch):
    _configure_gist_credentials(monkeypatch)
    response = _gist_response(
        gist_json={
            "files": {
                storage.GIST_FILENAME: {"content": json.dumps([1, 2, 3])}
            }
        }
    )
    get_mock = Mock(return_value=response)
    monkeypatch.setattr(storage.requests, "get", get_mock)

    assert storage.load() == DEFAULT_DATA
    get_mock.assert_called_once()


def test_load_parses_a_valid_gist(monkeypatch):
    _configure_gist_credentials(monkeypatch)
    today = date.today().isoformat()
    payload = {
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
        "history": [{"date": today, "solves": {"akshat": 2, "alice": 5}}],
    }
    response = _gist_response(
        gist_json={
            "files": {
                storage.GIST_FILENAME: {"content": json.dumps(payload)}
            }
        }
    )
    get_mock = Mock(return_value=response)
    monkeypatch.setattr(storage.requests, "get", get_mock)

    assert storage.load() == payload
    get_mock.assert_called_once()


def test_load_removes_unsupported_legacy_fields(monkeypatch):
    _configure_gist_credentials(monkeypatch)
    response = _gist_response(
        gist_json={
            "files": {
                storage.GIST_FILENAME: {
                    "content": json.dumps(
                        {
                            "users": {
                                "akshat": {
                                    "last_submission_ts": 123,
                                    "streak": 9,
                                    "last_solve_date": "2026-07-16",
                                    "daily_solves": {"2026-07-17": 3},
                                }
                            },
                            "history": [],
                        }
                    )
                }
            }
        }
    )
    get_mock = Mock(return_value=response)
    monkeypatch.setattr(storage.requests, "get", get_mock)

    assert storage.load() == {
        "users": {
            "akshat": {
                "last_submission_ts": 123,
                "daily_solves": {"2026-07-17": 3},
            }
        },
        "history": [],
    }
    get_mock.assert_called_once()


def test_load_normalizes_malformed_daily_solves(monkeypatch):
    _configure_gist_credentials(monkeypatch)
    response = _gist_response(
        gist_json={
            "files": {
                storage.GIST_FILENAME: {
                    "content": json.dumps(
                        {
                            "users": {
                                "akshat": {
                                    "last_submission_ts": 123,
                                    "daily_solves": "broken",
                                }
                            },
                            "history": [],
                        }
                    )
                }
            }
        }
    )
    get_mock = Mock(return_value=response)
    monkeypatch.setattr(storage.requests, "get", get_mock)

    assert storage.load() == {
        "users": {
            "akshat": {
                "last_submission_ts": 123,
                "daily_solves": {},
            }
        },
        "history": [],
    }
    get_mock.assert_called_once()


def test_save_sends_exactly_one_patch_request(monkeypatch):
    _configure_gist_credentials(monkeypatch)
    patch_mock = Mock(return_value=_gist_response(gist_json={}))
    monkeypatch.setattr(storage.requests, "patch", patch_mock)

    storage.save(_default_data())

    assert patch_mock.call_count == 1


def test_save_generates_the_expected_patch_payload(monkeypatch):
    _configure_gist_credentials(monkeypatch)
    patch_mock = Mock(return_value=_gist_response(gist_json={}))
    monkeypatch.setattr(storage.requests, "patch", patch_mock)

    data = {
        "users": {
            "akshat": {
                "last_submission_ts": 123,
                "daily_solves": {date.today().isoformat(): 2},
            }
        },
        "history": [],
    }

    storage.save(data)

    expected_payload = {
        "files": {
            storage.GIST_FILENAME: {
                "content": json.dumps(data, indent=2, ensure_ascii=False)
            }
        }
    }
    patch_mock.assert_called_once()
    _, kwargs = patch_mock.call_args
    assert kwargs["json"] == expected_payload


def test_save_does_nothing_when_gist_credentials_are_missing(monkeypatch):
    monkeypatch.setattr(storage.config, "GIST_ID", "")
    monkeypatch.setattr(storage.config, "GIST_TOKEN", "")
    patch_mock = Mock()
    monkeypatch.setattr(storage.requests, "patch", patch_mock)

    storage.save(_default_data())

    patch_mock.assert_not_called()


def test_save_gracefully_handles_timeout(monkeypatch):
    _configure_gist_credentials(monkeypatch)
    patch_mock = Mock(side_effect=requests.exceptions.Timeout())
    monkeypatch.setattr(storage.requests, "patch", patch_mock)

    storage.save(_default_data())

    patch_mock.assert_called_once()


def test_save_gracefully_handles_request_exception(monkeypatch):
    _configure_gist_credentials(monkeypatch)
    patch_mock = Mock(side_effect=requests.exceptions.RequestException())
    monkeypatch.setattr(storage.requests, "patch", patch_mock)

    storage.save(_default_data())

    patch_mock.assert_called_once()


def test_get_user_auto_creates_user():
    data = _default_data()

    user = storage.get_user(data, "akshat")

    assert data["users"]["akshat"] == {
        "last_submission_ts": 0,
        "daily_solves": {},
    }
    assert user == data["users"]["akshat"]


def test_get_user_can_add_multiple_users():
    data = _default_data()

    storage.get_user(data, "akshat")
    storage.get_user(data, "alice")

    assert set(data["users"].keys()) == {"akshat", "alice"}


def test_set_last_submission_ts_updates_the_record():
    data = _default_data()

    storage.set_last_submission_ts(data, "akshat", 12345)

    assert data["users"]["akshat"]["last_submission_ts"] == 12345
    assert storage.get_last_submission_ts(data, "akshat") == 12345


def test_get_last_submission_ts_defaults_to_zero():
    data = _default_data()

    assert storage.get_last_submission_ts(data, "akshat") == 0


def test_increment_daily_solves_increments_the_count():
    data = _default_data()

    count1 = storage.increment_daily_solves(data, "akshat")
    count2 = storage.increment_daily_solves(data, "akshat")
    today = date.today().isoformat()

    assert count1 == 1
    assert count2 == 2
    assert data["users"]["akshat"]["daily_solves"][today] == 2


def test_get_daily_solves_returns_the_requested_day():
    data = _default_data()
    today = date.today().isoformat()
    storage.get_user(data, "akshat")["daily_solves"][today] = 7

    assert storage.get_daily_solves(data, "akshat") == 7
    assert storage.get_daily_solves(data, "akshat", "2026-07-01") == 0


def test_record_history_appends_today_entry():
    today = date.today().isoformat()
    data = {
        "users": {
            "akshat": {
                "last_submission_ts": 0,
                "daily_solves": {today: 3},
            }
        },
        "history": [],
    }

    storage.record_history(data, ["akshat"])

    assert len(data["history"]) == 1
    assert data["history"][0] == {"date": today, "solves": {"akshat": 3}}


def test_record_history_updates_an_existing_day_entry_instead_of_appending():
    today = date.today().isoformat()
    data = {
        "users": {
            "akshat": {
                "last_submission_ts": 0,
                "daily_solves": {today: 4},
            }
        },
        "history": [
            {"date": today, "solves": {"akshat": 1}},
        ],
    }

    storage.record_history(data, ["akshat"])

    assert len(data["history"]) == 1
    assert data["history"][0] == {"date": today, "solves": {"akshat": 4}}


def test_record_history_caps_history_to_the_last_90_entries():
    today = date.today().isoformat()
    data = {
        "users": {
            "akshat": {
                "last_submission_ts": 0,
                "daily_solves": {today: 1},
            }
        },
        "history": [
            {"date": f"2026-01-{day:02d}", "solves": {"akshat": day}}
            for day in range(1, 91)
        ],
    }

    storage.record_history(data, ["akshat"])

    assert len(data["history"]) == 90
    assert data["history"][0]["date"] == "2026-01-02"
    assert data["history"][-1] == {"date": today, "solves": {"akshat": 1}}
