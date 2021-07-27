import datetime
from unittest.mock import MagicMock

import pytest
from wanikani_api.client import Client as WaniKaniClient
from pytest_mock import MockerFixture

from wanikani_notifier.wanikani import get_available_assignments, get_notification_message, AvailableAssignments


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


def test_available_assignments(mocked_wk_client):
    mocked_wk_client.assignments.return_value = []

    get_available_assignments(mocked_wk_client, datetime.datetime.utcnow())

    mocked_wk_client.assignments.assert_called()


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
