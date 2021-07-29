from typing import Dict, Any
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from tests.notifiers.test_notifier import NotifierTester
from wanikani_notifier.notifiers.notifier import Notifier
from wanikani_notifier.notifiers.pushover import PushoverNotifier


@pytest.fixture
def mocked_pushover_init(mocker: MockerFixture) -> MagicMock:
    mocked_app = mocker.patch("chump.Application")
    yield mocked_app
    mocked_app.assert_called_once()
    mocked_app.return_value.get_user.assert_called_once()


@pytest.fixture
def mocked_pushover_send_message(mocked_pushover_init) -> MagicMock:
    return mocked_pushover_init.return_value.get_user.return_value.send_message


class TestPushoverNotifier(NotifierTester):
    @property
    def key(self) -> str:
        return "pushover"

    @pytest.fixture
    def build_parameters(self, mocked_pushover_init) -> Dict[str, Any]:
        return {"app_token": "__TOKEN__", "user_token": "__TOKEN__"}

    @pytest.fixture
    def imp(self, mocked_pushover_init) -> Notifier:
        yield PushoverNotifier("__TOKEN__", "__TOKEN__")

    def test_notify_simple_message(self, imp, mocked_pushover_send_message):
        super().test_notify_simple_message(imp)
        mocked_pushover_send_message.assert_called()

    def test_notify_message_all_options(self, imp, mocked_pushover_send_message):
        super().test_notify_message_all_options(imp)
        mocked_pushover_send_message.assert_called()
