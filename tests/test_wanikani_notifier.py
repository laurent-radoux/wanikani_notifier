from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from wanikani_notifier.wanikani_notifier import notify_new_assignments


class MockedLesson:
    def __init__(self):
        self.unlocked_at = True
        self.started_at = False


class MockedReview:
    def __init__(self):
        self.unlocked_at = True
        self.started_at = True


@pytest.fixture
def mocked_wk_client(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("wanikani_api.client.Client")


@pytest.fixture
def mocked_pushsafer_init(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("pushsafer.init")


@pytest.fixture
def mocked_pushsafer_send_message(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("pushsafer.Client.send_message")


def test_notify_no_new_assignment(mocked_wk_client, mocked_pushsafer_init, mocked_pushsafer_send_message):
    mocked_wk_client.return_value.assignments.return_value = []

    notify_new_assignments("wk_token", "ps_token", None)

    mocked_wk_client.assert_called_once()
    mocked_wk_client.return_value.assignments.assert_called_once()
    mocked_pushsafer_init.assert_called_once()
    mocked_pushsafer_send_message.assert_not_called()


def test_notify_new_reviews_no_new_lessons(mocked_wk_client, mocked_pushsafer_init, mocked_pushsafer_send_message):
    mocked_wk_client.return_value.assignments.return_value = [MockedReview()]

    notify_new_assignments("wk_token", "ps_token", None)

    mocked_wk_client.assert_called_once()
    mocked_wk_client.return_value.assignments.assert_called_once()
    mocked_pushsafer_init.assert_called_once()
    mocked_pushsafer_send_message.assert_called_once()
    assert "lesson" not in mocked_pushsafer_send_message.call_args.args[0]
    assert "review" in mocked_pushsafer_send_message.call_args.args[0]


def test_notify_no_new_reviews_new_lessons(mocked_wk_client, mocked_pushsafer_init, mocked_pushsafer_send_message):
    mocked_wk_client.return_value.assignments.return_value = [MockedLesson()]

    notify_new_assignments("wk_token", "ps_token", None)

    mocked_wk_client.assert_called_once()
    mocked_wk_client.return_value.assignments.assert_called_once()
    mocked_pushsafer_init.assert_called_once()
    mocked_pushsafer_send_message.assert_called_once()
    assert "lesson" in mocked_pushsafer_send_message.call_args.args[0]
    assert "review" not in mocked_pushsafer_send_message.call_args.args[0]


def test_notify_new_reviews_new_lessons(mocked_wk_client, mocked_pushsafer_init, mocked_pushsafer_send_message):
    mocked_wk_client.return_value.assignments.return_value = [MockedReview(), MockedLesson()]

    notify_new_assignments("wk_token", "ps_token", None)

    mocked_wk_client.assert_called_once()
    mocked_wk_client.return_value.assignments.assert_called_once()
    mocked_pushsafer_init.assert_called_once()
    mocked_pushsafer_send_message.assert_called_once()
    assert "lesson" in mocked_pushsafer_send_message.call_args.args[0]
    assert "review" in mocked_pushsafer_send_message.call_args.args[0]
