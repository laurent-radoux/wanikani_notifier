from typing import Dict, Any
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from tests.notifiers.test_notifier import NotifierTester
from wanikani_notifier.notifiers.notifier import Notifier
from wanikani_notifier.notifiers.pushsafer import PushSaferNotifier


@pytest.fixture
def mocked_pushsafer_init(mocker: MockerFixture) -> MagicMock:
    mocked = mocker.patch("pushsafer.Client")
    yield mocked
    mocked.assert_called_once()


@pytest.fixture
def mocked_pushsafer_send_message(mocked_pushsafer_init) -> MagicMock:
    return mocked_pushsafer_init.return_value.send_message


class TestPushSaferNotifier(NotifierTester):
    @property
    def key(self) -> str:
        return "pushsafer"

    @pytest.fixture
    def build_parameters(self) -> Dict[str, Any]:
        return {"private_key": "__TOKEN__"}

    @pytest.fixture
    def imp(self, mocked_pushsafer_init) -> Notifier:
        yield PushSaferNotifier("__TOKEN__")

    def test_notify_simple_message(self, imp, mocked_pushsafer_send_message):
        super().test_notify_simple_message(imp)
        mocked_pushsafer_send_message.assert_called()

    def test_notify_message_all_options(self, imp, mocked_pushsafer_send_message):
        super().test_notify_message_all_options(imp)
        mocked_pushsafer_send_message.assert_called()
