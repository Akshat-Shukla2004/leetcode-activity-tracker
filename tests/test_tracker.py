from backend import tracker


def test_get_user_inactive_minutes_no_baseline(mocker):
    mocker.patch(
        "backend.tracker.storage.get_last_submission_ts",
        return_value=0,
    )

    assert tracker._get_user_inactive_minutes({}) == 0


def test_get_user_inactive_minutes(mocker):
    mocker.patch(
        "backend.tracker.storage.get_last_submission_ts",
        return_value=100,
    )

    mocker.patch(
        "backend.tracker.leetcode.minutes_ago",
        return_value=42,
    )

    assert tracker._get_user_inactive_minutes({}) == 42


def test_check_opponent_initializes_baseline(mocker):
    data = {}

    mocker.patch(
        "backend.tracker.storage.get_last_submission_ts",
        return_value=0,
    )

    mocker.patch(
        "backend.tracker.leetcode.get_latest_accepted",
        return_value={
            "title": "Two Sum",
            "timestamp": 100,
        },
    )

    set_ts = mocker.patch(
        "backend.tracker.storage.set_last_submission_ts"
    )

    result = tracker.check_opponent(data, "alice")

    assert result == 0
    set_ts.assert_called_once_with(data, "alice", 100)


def test_check_opponent_no_new_submissions(mocker):
    data = {}

    mocker.patch(
        "backend.tracker.storage.get_last_submission_ts",
        return_value=100,
    )

    mocker.patch(
        "backend.tracker.leetcode.get_accepted_submissions_since",
        return_value=[],
    )

    assert tracker.check_opponent(data, "alice") == 0


def test_check_opponent_new_submission(mocker):
    data = {}

    mocker.patch(
        "backend.tracker.storage.get_last_submission_ts",
        return_value=100,
    )

    mocker.patch(
        "backend.tracker.leetcode.get_accepted_submissions_since",
        return_value=[
            {
                "title": "Two Sum",
                "timestamp": 200,
            }
        ],
    )

    mocker.patch(
        "backend.tracker.leetcode.seconds_ago",
        return_value=10,
    )

    mocker.patch(
        "backend.tracker.storage.increment_daily_solves",
        return_value=1,
    )

    mocker.patch(
        "backend.tracker.messages.generate_alert_message",
        return_value="hello",
    )

    send = mocker.patch(
        "backend.tracker.notifier.send_alert",
        return_value=True,
    )

    mocker.patch(
        "backend.tracker.storage.set_last_submission_ts",
    )

    result = tracker.check_opponent(data, "alice")

    assert result == 1
    send.assert_called_once()


def test_check_user_inactivity_no_baseline(mocker):
    data = {}

    mocker.patch(
        "backend.tracker.storage.get_last_submission_ts",
        return_value=0,
    )

    send = mocker.patch(
        "backend.tracker.notifier.send_silent"
    )

    tracker.check_user_inactivity(data)

    send.assert_not_called()


def test_sync_my_activity_first_run(mocker):
    data = {}

    mocker.patch(
        "backend.tracker.leetcode.get_latest_accepted",
        return_value={
            "title": "Two Sum",
            "timestamp": 100,
        },
    )

    mocker.patch(
        "backend.tracker.storage.get_last_submission_ts",
        return_value=0,
    )

    set_ts = mocker.patch(
        "backend.tracker.storage.set_last_submission_ts"
    )

    tracker.sync_my_activity(data)

    set_ts.assert_called_once()


def test_run_check_cycle(mocker):
    data = {}

    mocker.patch(
        "backend.tracker.storage.load",
        return_value=data,
    )

    mocker.patch(
        "backend.tracker.sync_my_activity",
    )

    mocker.patch(
        "backend.tracker.check_opponent",
        return_value=0,
    )

    mocker.patch(
        "backend.tracker.check_user_inactivity",
    )

    mocker.patch(
        "backend.tracker.storage.record_history",
    )

    save = mocker.patch(
        "backend.tracker.storage.save",
    )

    tracker.run_check_cycle()

    save.assert_called_once_with(data)