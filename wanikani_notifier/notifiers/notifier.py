from abc import ABC, abstractmethod
from typing import Callable, Optional


class NoMessageProvided(RuntimeError):
    pass


class Notifier(ABC):
    @property
    @abstractmethod
    def key(self) -> str:
        """
        Defines the key used to identify a particular notifier class.
        :return: the key string identifying a particular notifier class.
        """

    @abstractmethod
    def notify(self, title: str, message: str, url: Optional[str] = None, icon: Optional[str] = None):
        """
        Sends a notification.

        :param title: Title of the notification to send.
        :param message: Content of the notification to send.
        :param url: Optional url to display.
        :param icon: Optional icon to display
        """


class NotifierFactory:
    def __init__(self):
        self._builders = {}

    def register_builder(self, key: str, builder: Callable) -> None:
        self._builders[key] = builder

    def create(self, key: str, **kwargs) -> Notifier:
        return self._builders[key.lower()](**kwargs)


factory = NotifierFactory()
