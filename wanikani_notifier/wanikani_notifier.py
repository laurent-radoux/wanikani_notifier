import datetime
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from wanikani_api import client as wk_client
import pushsafer


def send_notification(client: pushsafer.Client, title: str, message: str) -> None:
    """
    Sends a notification via PushSafer.

    :param client: Pushsafer client (must have been init).
    :param title: Title of the notification.
    :param message: Message contained in the notification.
    """
    client.send_message(message, title,
                        None, None, None, None, None, None, None,
                        None, None, None, None, None, None, None)


def notify_available_assignments(wanikani_token: str, pushsafer_token: str, hours_ago: int) -> None:
    """
    Fetches the list of new assignments from WaniKani and notifies when at least one review or
    one lesson is available.

    :param wanikani_token: Private API token to connect to WaniKani API
    :param pushsafer_token: Private key to connect to PushSafer API
    :param hours_ago: Specifies how far back in time available assignment should be retrieved,
                        in hours (-1 indicates infinity).
    """
    urllib3.disable_warnings(category=InsecureRequestWarning)
    wk_api = wk_client.Client(wanikani_token)
    pushsafer.init(pushsafer_token)

    review_time = datetime.datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    assignments = wk_api.assignments(fetch_all=True,
                                     available_before=review_time,
                                     available_after=(
                                         review_time - datetime.timedelta(hours=hours_ago)
                                         if hours_ago >= 0
                                         else None
                                     )
                                     )

    review_count = sum(1 for a in assignments if a.started_at)
    lesson_count = sum(1 for a in assignments if a.unlocked_at and not a.started_at)

    if review_count + lesson_count > 0:
        if review_count == 0:
            message = f"{lesson_count} lessons are available!"
        elif lesson_count == 0:
            message = f"{review_count} reviews are available!"
        else:
            message = f"{review_count} reviews and {lesson_count} lessons are available!"

        send_notification(pushsafer.Client(""), "WaniKani", message)
