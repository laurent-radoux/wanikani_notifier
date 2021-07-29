from typing import Optional

from wanikani_notifier.notifiers.notifier import Notifier, NoMessageProvided, factory


class ConsoleNotifier(Notifier):
    @classmethod
    def build(cls, **_ignored) -> "ConsoleNotifier":
        return ConsoleNotifier()

    @classmethod
    def key(cls) -> str:
        return "console"

    def notify(self, title: str, message: str, url: Optional[str] = None, icon: Optional[str] = None):
        if not message:
            raise NoMessageProvided

        notification = f"{title}:\n{message}"
        if url:
            notification += f"\n{url}"

        print(notification)


factory.register_builder(ConsoleNotifier.key(), ConsoleNotifier.build)
