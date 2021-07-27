from wanikani_notifier.notifiers.notifier import Notifier, NoMessageProvided, factory


class ConsoleNotifier(Notifier):
    @classmethod
    def build(cls, **_ignored) -> "ConsoleNotifier":
        return ConsoleNotifier()

    @classmethod
    def key(cls) -> str:
        return "console"

    def notify(self, title: str, message: str):
        if not message:
            raise NoMessageProvided

        print(f"{title}: {message}")


factory.register_builder(ConsoleNotifier.key(), ConsoleNotifier.build)
