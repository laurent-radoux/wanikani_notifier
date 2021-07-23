from datetime import datetime, timedelta
from collections import namedtuple
from typing import List, Optional

from wanikani_api.client import Client as WaniKaniClient

from wanikani_notifier.notifiers.notifier import Notifier

AvailableAssignments = namedtuple("AvailableAssignments", ("reviews", "lessons"))


def get_available_assignments(wanikani_client: WaniKaniClient, start: datetime, end: datetime) -> AvailableAssignments:
    """
    Gets the number of reviews and lessons that are available in the provided time period.

    :param wanikani_client: WaniKani client to use for fetching assignments
    :param start: Start of the time period when assignments are considered (inclusive).
    :param end: End of the time period when assignments are considered (inclusive).
    :return: the available assignments.
    """
    assignments = wanikani_client.assignments(fetch_all=True, available_after=start, available_before=end)

    review_count = sum(1 for a in assignments if a.started_at)
    lesson_count = sum(1 for a in assignments if a.unlocked_at and not a.started_at)

    return AvailableAssignments(reviews=review_count, lessons=lesson_count)


def get_notification_message(available_assignments: AvailableAssignments) -> Optional[str]:
    """
    Creates the notification message corresponding to the available assignments.

    :param available_assignments: Number of reviews and lessons that are available.
    :return: a string containing the notification message to send if at least one assignment is available,
                None otherwise
    """
    if not sum(available_assignments):
        return

    if not available_assignments.reviews:
        return f"{available_assignments.lessons} lessons are available!"
    elif not available_assignments.lessons:
        return f"{available_assignments.reviews} reviews are available!"
    else:
        return f"{available_assignments.reviews} reviews and {available_assignments.lessons} lessons are available!"


def notify_available_assignments(wanikani_client: WaniKaniClient, since_x_hours: int, notifiers: List[Notifier]) -> None:
    """
    Fetches the list of new assignments from WaniKani and notifies when at least one review or
    one lesson is available as of when the function is called and since some amount of hours.

    :param wanikani_client: WaniKani client to use for fetching assignments.
    :param since_x_hours: How many hours since available assignments should be retrieved, -1 representing since forever.
    :param notifiers: List of notifiers that can send a notification if some assignements are available.
    """

    current_time_rounded = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    available_assignments = get_available_assignments(wanikani_client,
                                                      start=(
                                                          current_time_rounded - (
                                                                  timedelta(hours=since_x_hours) - timedelta(seconds=1))
                                                          if since_x_hours >= 0
                                                          else None
                                                      ),
                                                      end=current_time_rounded
                                                      )

    message = get_notification_message(available_assignments)
    if message:
        for n in notifiers:
            n.notify("WaniKani!", message)
