import pushsafer
import urllib3
from urllib3.exceptions import InsecureRequestWarning

from wanikani_notifier.notifiers.notifier import Notifier, NoMessageProvided


class PushSaferNotifier(Notifier):
    def __init__(self, private_key: str):
        urllib3.disable_warnings(category=InsecureRequestWarning)

        pushsafer.init(private_key)
        self._client = pushsafer.Client("")

    def notify(self, title: str, message: str):
        if not message:
            raise NoMessageProvided

        self._client.send_message(message, title,
                                  None, None, None, None, None, None, None,
                                  None, None, None, None, None, None, None)
