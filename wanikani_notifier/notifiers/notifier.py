from abc import ABC, abstractmethod


class NoMessageProvided(RuntimeError):
    pass


class Notifier(ABC):
    @abstractmethod
    def notify(self, title: str, message: str):
        """
        Sends a notification.

        :param title: Title of the notification to send.
        :param message: Content of the notification to send.
        """
