import requests

from backend import leetcode


class MockResponse:
    def __init__(self, json_data=None, status_code=200):
        self._json = json_data or {}
        self.status_code = status_code

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError()


def test_fetch_accepted_submissions_success(mocker):
    response = MockResponse(
        {
            "data": {
                "recentSubmissionList": [
                    {
                        "title": "Two Sum",
                        "titleSlug": "two-sum",
                        "timestamp": "100",
                        "statusDisplay": "Accepted",
                        "lang": "python",
                    },
                    {
                        "title": "Add Two Numbers",
                        "titleSlug": "add-two-numbers",
                        "timestamp": "200",
                        "statusDisplay": "Wrong Answer",
                        "lang": "python",
                    },
                ]
            }
        }
    )

    mocker.patch("backend.leetcode.requests.post", return_value=response)

    subs = leetcode.fetch_accepted_submissions("akshat")

    assert len(subs) == 1
    assert subs[0]["title"] == "Two Sum"
    assert subs[0]["timestamp"] == 100


def test_fetch_timeout_returns_empty(mocker):
    mocker.patch(
        "backend.leetcode.requests.post",
        side_effect=requests.exceptions.Timeout,
    )

    assert leetcode.fetch_accepted_submissions("akshat") == []


def test_fetch_request_exception_returns_empty(mocker):
    mocker.patch(
        "backend.leetcode.requests.post",
        side_effect=requests.exceptions.RequestException,
    )

    assert leetcode.fetch_accepted_submissions("akshat") == []


def test_fetch_empty_graphql_response_returns_empty(mocker):
    response = MockResponse({"data": {}})

    mocker.patch("backend.leetcode.requests.post", return_value=response)

    assert leetcode.fetch_accepted_submissions("akshat") == []


def test_fetch_skips_malformed_accepted_entries(mocker):
    response = MockResponse(
        {
            "data": {
                "recentSubmissionList": [
                    {
                        "title": "Valid",
                        "titleSlug": "valid",
                        "timestamp": "100",
                        "statusDisplay": "Accepted",
                        "lang": "python",
                    },
                    {
                        "title": "Broken",
                        "titleSlug": "broken",
                        "timestamp": "not-a-number",
                        "statusDisplay": "Accepted",
                        "lang": "python",
                    },
                ]
            }
        }
    )

    mocker.patch("backend.leetcode.requests.post", return_value=response)

    subs = leetcode.fetch_accepted_submissions("akshat")

    assert len(subs) == 1
    assert subs[0]["title"] == "Valid"


def test_get_latest_accepted(mocker):
    mocker.patch(
        "backend.leetcode.fetch_accepted_submissions",
        return_value=[
            {
                "title": "A",
                "timestamp": 10,
            },
            {
                "title": "B",
                "timestamp": 30,
            },
            {
                "title": "C",
                "timestamp": 20,
            },
        ],
    )

    latest = leetcode.get_latest_accepted("akshat")

    assert latest["title"] == "B"


def test_get_latest_returns_none(mocker):
    mocker.patch(
        "backend.leetcode.fetch_accepted_submissions",
        return_value=[],
    )

    assert leetcode.get_latest_accepted("akshat") is None


def test_get_accepted_since(mocker):
    mocker.patch(
        "backend.leetcode.fetch_accepted_submissions",
        return_value=[
            {"title": "A", "timestamp": 5},
            {"title": "B", "timestamp": 25},
            {"title": "C", "timestamp": 15},
        ],
    )

    result = leetcode.get_accepted_submissions_since(
        "akshat",
        since_ts=10,
    )

    assert len(result) == 2
    assert result[0]["timestamp"] == 15
    assert result[1]["timestamp"] == 25


def test_get_accepted_since_filters_duplicate_timestamps(mocker):
    mocker.patch(
        "backend.leetcode.fetch_accepted_submissions",
        return_value=[
            {"title": "A", "timestamp": 10},
            {"title": "B", "timestamp": 10},
            {"title": "C", "timestamp": 20},
        ],
    )

    result = leetcode.get_accepted_submissions_since(
        "akshat",
        since_ts=10,
    )

    assert [item["timestamp"] for item in result] == [20]


def test_seconds_ago():
    now = leetcode.time.time()

    seconds = leetcode.seconds_ago(int(now) - 5)

    assert 4 <= seconds <= 6


def test_minutes_ago():
    now = leetcode.time.time()

    minutes = leetcode.minutes_ago(int(now) - 180)

    assert minutes == 3