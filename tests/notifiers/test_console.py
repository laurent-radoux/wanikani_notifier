from typing import Any, Dict
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from tests.notifiers.test_notifier import NotifierTester
from wanikani_notifier.notifiers.console import ConsoleNotifier
from wanikani_notifier.notifiers.notifier import Notifier


@pytest.fixture
def mocked_console_print(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("builtins.print")


class TestConsoleNotifier(NotifierTester):
    @property
    def key(self) -> str:
        return "console"

    @pytest.fixture
    def build_parameters(self) -> Dict[str, Any]:
        return {}

    @pytest.fixture
    def imp(self, mocked_console_print) -> Notifier:
        yield ConsoleNotifier()

    def test_notify_simple_message(self, imp, mocked_console_print):
        super().test_notify_simple_message(imp)
        mocked_console_print.assert_called()

    def test_notify_message_all_options(self, imp, mocked_console_print):
        super().test_notify_message_all_options(imp)
        mocked_console_print.assert_called()
