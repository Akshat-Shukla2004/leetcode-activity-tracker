import requests

from backend import notifier


class MockResponse:
    def __init__(self, json_data=None, status_code=200):
        self._json = json_data or {"ok": True}
        self.status_code = status_code

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError()


def test_telegram_api_url(monkeypatch):
    monkeypatch.setattr(notifier.config, "BOT_TOKEN", "TEST_TOKEN")

    url = notifier._telegram_api_url("sendMessage")

    assert url == "https://api.telegram.org/botTEST_TOKEN/sendMessage"


def test_send_raw_success(mocker):
    response = MockResponse({"ok": True})

    mocker.patch(
        "backend.notifier.requests.post",
        return_value=response,
    )

    assert (
        notifier._send_raw(
            "Hello",
            disable_notification=False,
        )
        is True
    )


def test_send_raw_http_failure(mocker):
    mocker.patch(
        "backend.notifier.requests.post",
        side_effect=requests.RequestException,
    )

    assert (
        notifier._send_raw(
            "Hello",
            disable_notification=False,
        )
        is False
    )


def test_send_raw_invalid_json(mocker):
    class BadResponse:
        def raise_for_status(self):
            pass

        def json(self):
            raise ValueError()

    mocker.patch(
        "backend.notifier.requests.post",
        return_value=BadResponse(),
    )

    assert (
        notifier._send_raw(
            "Hello",
            disable_notification=False,
        )
        is False
    )


def test_send_raw_api_failure(mocker):
    response = MockResponse({"ok": False})

    mocker.patch(
        "backend.notifier.requests.post",
        return_value=response,
    )

    assert (
        notifier._send_raw(
            "Hello",
            disable_notification=False,
        )
        is False
    )


def test_send_alert_calls_send_raw(mocker):
    mocked = mocker.patch(
        "backend.notifier._send_raw",
        return_value=True,
    )

    notifier.send_alert("Test")

    mocked.assert_called_once_with(
        "Test",
        disable_notification=False,
    )


def test_send_silent_calls_send_raw(mocker):
    mocked = mocker.patch(
        "backend.notifier._send_raw",
        return_value=True,
    )

    notifier.send_silent("Test")

    mocked.assert_called_once_with(
        "Test",
        disable_notification=True,
    )
