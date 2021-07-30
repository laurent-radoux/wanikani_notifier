from abc import ABC, abstractmethod
from typing import Any, Dict

import pytest

from wanikani_notifier.notifiers.notifier import NoMessageProvided, Notifier, factory


class NotifierTester(ABC):
    @abstractmethod
    @pytest.fixture
    def imp(self) -> Notifier:
        pass

    @classmethod
    @abstractmethod
    def key(cls) -> str:
        pass

    @abstractmethod
    @pytest.fixture
    def build_parameters(self) -> Dict[str, Any]:
        pass

    def test_builder(self, build_parameters):
        assert factory.create(self.key, **build_parameters) is not None

    def test_notify_none_message(self, imp):
        with pytest.raises(NoMessageProvided):
            imp.notify("title", None)

    def test_notify_empty_message(self, imp):
        with pytest.raises(NoMessageProvided):
            imp.notify("title", "")

    def test_notify_simple_message(self, imp):
        imp.notify("title", "message")

    def test_notify_message_all_options(self, imp):
        imp.notify("title", "message", "url", "icon")
