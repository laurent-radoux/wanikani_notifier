from typing import Optional

import pushsafer

from wanikani_notifier.notifiers.notifier import Notifier, NoMessageProvided, factory


class PushSaferNotifier(Notifier):
    def __init__(self, private_key: str):
        self._client = pushsafer.Client(private_key)

    @classmethod
    def key(cls) -> str:
        return "pushsafer"

    @classmethod
    def build(cls, private_key: str, **_ignored) -> "PushSaferNotifier":
        return PushSaferNotifier(private_key)

    def notify(self, title: str, message: str, url: Optional[str] = None, icon: Optional[str] = None):
        if not message:
            raise NoMessageProvided

        self._client.send_message(title=title, message=message, url=url)


factory.register_builder(PushSaferNotifier.key(), PushSaferNotifier.build)
