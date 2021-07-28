import chump

from wanikani_notifier.notifiers.notifier import Notifier, NoMessageProvided, factory


class PushoverNotifier(Notifier):
    def __init__(self, app_token: str, user_token: str):
        self._app = chump.Application(app_token)
        self._user = self._app.get_user(user_token)

    @classmethod
    def key(cls) -> str:
        return "pushover"

    @classmethod
    def build(cls, app_token: str, user_token: str, **_ignored) -> "PushoverNotifier":
        return PushoverNotifier(app_token, user_token)

    def notify(self, title: str, message: str):
        if not message:
            raise NoMessageProvided

        self._user.send_message(message, title=title)


factory.register_builder(PushoverNotifier.key(), PushoverNotifier.build)
