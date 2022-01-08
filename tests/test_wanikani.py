import datetime
from dataclasses import dataclass
from unittest.mock import MagicMock

import pytest
from wanikani_api.client import Client as WaniKaniClient
from pytest_mock import MockerFixture

from wanikani_notifier.wanikani import get_all_subjects
from wanikani_notifier.wanikani import get_available_assignments, get_notification_message, AvailableAssignments


@dataclass
class MockedLesson:
    unlocked_at = True
    started_at = False


@dataclass
class MockedReview:
    unlocked_at = True
    started_at = True


class MockedSubject:
    def __init__(self, id: int, data_updated_at: datetime):
        self.id = id
        self.data_updated_at = data_updated_at
        self._raw = {}


@pytest.fixture
def mocked_wk_client(mocker: MockerFixture) -> MagicMock:
    return mocker.Mock(spec=WaniKaniClient)


@pytest.fixture
def mocked_os(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("wanikani_notifier.wanikani.os")


@pytest.fixture
def mocked_open(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("builtins.open")


@pytest.fixture
def mocked_json(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("wanikani_notifier.wanikani.ujson")


@pytest.fixture
def mocked_subject(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("wanikani_notifier.wanikani.Subject")


def test_get_all_subjects_folder_not_found(mocked_wk_client,
                                           mocked_os, mocked_open,
                                           mocked_json):
    mocked_os.path.exists.return_value = False
    mocked_json.load.return_value = {}
    mocked_wk_client.subjects.return_value = [
        MockedSubject(id=1, data_updated_at=datetime.datetime(year=2022, month=1, day=1)),
        MockedSubject(id=2, data_updated_at=datetime.datetime(year=2021, month=1, day=1)),
        MockedSubject(id=3, data_updated_at=datetime.datetime(year=2021, month=1, day=1)),
    ]

    get_all_subjects(mocked_wk_client)

    assert mocked_os.path.exists.call_count == 2
    mocked_os.makedirs.assert_called()
    mocked_wk_client.subjects.assert_called()
    mocked_json.load.assert_not_called()
    mocked_json.dump.assert_called()


def test_get_all_subjects_folder_found_no_subject_cached(mocked_wk_client,
                                                         mocked_os, mocked_open,
                                                         mocked_json):
    mocked_os.path.exists.return_value = True
    mocked_json.load.return_value = {}
    mocked_wk_client.subjects.return_value = [
        MockedSubject(id=1, data_updated_at=datetime.datetime(year=2022, month=1, day=1)),
        MockedSubject(id=2, data_updated_at=datetime.datetime(year=2021, month=1, day=1)),
        MockedSubject(id=3, data_updated_at=datetime.datetime(year=2021, month=1, day=1)),
    ]

    get_all_subjects(mocked_wk_client)

    assert mocked_os.path.exists.call_count == 2
    mocked_os.makedirs.assert_not_called()
    mocked_wk_client.subjects.assert_called()
    mocked_json.load.assert_called()
    mocked_json.dump.assert_called()


def test_get_all_subjects_some_subjects_cached(mocked_wk_client,
                                               mocked_os, mocked_open,
                                               mocked_json, mocked_subject):
    mocked_os.path.exists.return_value = True
    mocked_json.load.return_value = [
        {"id": 1, "data_updated_at": "2021-12-27"},
        {"id": 2, "data_updated_at": "2021-12-28"},
    ]
    mocked_subject.return_value.data_updated_at = datetime.datetime(year=2021, month=12, day=12)
    mocked_wk_client.subjects.return_value = [
        MockedSubject(id=1, data_updated_at=datetime.datetime(year=2022, month=1, day=1)),
        MockedSubject(id=2, data_updated_at=datetime.datetime(year=2021, month=1, day=1)),
        MockedSubject(id=3, data_updated_at=datetime.datetime(year=2021, month=1, day=1)),
    ]

    get_all_subjects(mocked_wk_client)

    assert mocked_os.path.exists.call_count == 2
    mocked_os.makedirs.assert_not_called()
    mocked_wk_client.subjects.assert_called()
    mocked_json.load.assert_called()
    mocked_json.dump.assert_called()


def test_available_assignments_none(mocked_wk_client):
    mocked_wk_client.assignments.return_value = []

    get_available_assignments(mocked_wk_client, {}, datetime.datetime.utcnow())

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
