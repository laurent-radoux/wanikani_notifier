from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from tests.notifiers.test_notifier import NotifierTester
from wanikani_notifier.notifiers.notifier import Notifier
from wanikani_notifier.notifiers.pushsafer import PushSaferNotifier


@pytest.fixture
def mocked_pushsafer_init(mocker: MockerFixture) -> MagicMock:
    mocked = mocker.patch("pushsafer.init")
    yield mocked
    mocked.assert_called_once()


@pytest.fixture
def mocked_pushsafer_send_message(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("pushsafer.Client.send_message")


@pytest.fixture
def pushsafer_notifier(mocked_pushsafer_init, mocked_pushsafer_send_message) -> Notifier:
    return PushSaferNotifier("__TOKEN__")


class TestPushSaferNotifier(NotifierTester):
    @pytest.fixture
    def imp(self, mocked_pushsafer_init, mocked_pushsafer_send_message) -> Notifier:
        yield PushSaferNotifier("__TOKEN__")

    def test_notify_message(self, imp, mocked_pushsafer_send_message):
        super().test_notify_message(imp)
        mocked_pushsafer_send_message.assert_called()