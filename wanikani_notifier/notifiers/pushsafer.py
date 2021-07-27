import pushsafer
import urllib3
from urllib3.exceptions import InsecureRequestWarning

from wanikani_notifier.notifiers.notifier import Notifier, NoMessageProvided, factory


class PushSaferNotifier(Notifier):
    def __init__(self, private_key: str):
        urllib3.disable_warnings(category=InsecureRequestWarning)

        pushsafer.init(private_key)
        self._client = pushsafer.Client("")

    @classmethod
    def key(cls) -> str:
        return "pushsafer"

    @classmethod
    def build(cls, private_key: str, **_ignored) -> "PushSaferNotifier":
        return PushSaferNotifier(private_key)

    def notify(self, title: str, message: str):
        if not message:
            raise NoMessageProvided

        self._client.send_message(message, title,
                                  None, None, None, None, None, None, None,
                                  None, None, None, None, None, None, None)


factory.register_builder(PushSaferNotifier.key(), PushSaferNotifier.build)
