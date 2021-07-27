from wanikani_notifier.notifiers.notifier import Notifier, NoMessageProvided


class ConsoleNotifier(Notifier):
    def notify(self, title: str, message: str):
        if not message:
            raise NoMessageProvided

        print(f"{title}: {message}")
