from unittest.mock import MagicMock

import pytest
from wanikani_api.client import Client as WaniKaniClient
from pytest_mock import MockerFixture

from wanikani_notifier.notifiers.notifier import Notifier
from wanikani_notifier.wanikani_notifier import notify_available_assignments, get_notification_message, \
    AvailableAssignments


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
    return mocker.Mock(spec=WaniKaniClient)


@pytest.fixture
def mocked_notifier(mocker: MockerFixture) -> MagicMock:
    return mocker.Mock(spec=Notifier)


def test_notify_no_new_assignment(mocked_wk_client, mocked_notifier):
    mocked_wk_client.assignments.return_value = []

    notify_available_assignments(mocked_wk_client, -1, [mocked_notifier])

    mocked_wk_client.assignments.assert_called()
    mocked_notifier.notify.assert_not_called()


def test_notify_new_assignments_multiple_notifiers(mocked_wk_client, mocked_notifier):
    mocked_wk_client.assignments.return_value = [MockedLesson(), MockedLesson(), MockedReview()]

    notifiers = [mocked_notifier, mocked_notifier, mocked_notifier]
    notify_available_assignments(mocked_wk_client, -1, notifiers)

    mocked_wk_client.assignments.assert_called()
    mocked_notifier.notify.assert_called()
    assert mocked_notifier.notify.call_count == len(notifiers)


def test_notify_new_assignments_no_notifiers(mocked_wk_client, mocked_notifier):
    mocked_wk_client.assignments.return_value = [MockedLesson(), MockedLesson(), MockedReview()]

    notify_available_assignments(mocked_wk_client, -1, [])

    mocked_wk_client.assignments.assert_called()
    mocked_notifier.notify.assert_not_called()


def test_get_message_no_new_reviews_no_new_lessons():
    message = get_notification_message(AvailableAssignments(reviews=0, lessons=0))

    assert message is None


def test_get_message_new_reviews_no_new_lessons():
    message = get_notification_message(AvailableAssignments(reviews=2, lessons=0))

    assert "lesson" not in message
    assert "review" in message


def test_get_message_no_new_reviews_new_lessons():
    message = get_notification_message(AvailableAssignments(reviews=0, lessons=3))

    assert "lesson" in message
    assert "review" not in message


def test_get_message_new_reviews_new_lessons():
    message = get_notification_message(AvailableAssignments(reviews=2, lessons=3))

    assert "lesson" in message
    assert "review" in message
