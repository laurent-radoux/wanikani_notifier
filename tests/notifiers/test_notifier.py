from abc import ABC, abstractmethod

import pytest

from wanikani_notifier.notifiers.notifier import NoMessageProvided, Notifier


class NotifierTester(ABC):
    @abstractmethod
    @pytest.fixture
    def imp(self) -> Notifier:
        pass

    def test_notify_none_message(self, imp):
        with pytest.raises(NoMessageProvided):
            imp.notify("title", None)

    def test_notify_empty_message(self, imp):
        with pytest.raises(NoMessageProvided):
            imp.notify("title", "")

    def test_notify_message(self, imp):
        imp.notify("title", "message")
