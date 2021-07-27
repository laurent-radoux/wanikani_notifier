from datetime import datetime
from collections import namedtuple
from typing import Optional

from wanikani_api.client import Client as WaniKaniClient

AvailableAssignments = namedtuple("AvailableAssignments", ("reviews", "lessons"))


def get_available_assignments(wanikani_client: WaniKaniClient,
                              end: datetime,
                              start: datetime = None
                              ) -> AvailableAssignments:
    """
    Gets the number of reviews and lessons that are available in the provided time period.

    :rtype: object
    :param wanikani_client: WaniKani client to use for fetching assignments
    :param start: Start of the time period when assignments are considered (inclusive).
    :param end: End of the time period when assignments are considered (inclusive).
    :return: the available assignments.
    """
    assignments = wanikani_client.assignments(fetch_all=True, available_after=start, available_before=end)

    review_count = sum(1 for a in assignments if a.started_at)
    lesson_count = sum(1 for a in assignments if a.unlocked_at and not a.started_at)

    return AvailableAssignments(reviews=review_count, lessons=lesson_count)


def get_notification_message(available_assignments: AvailableAssignments,
                             message_template: Optional[str] = None) -> Optional[str]:
    """
    Creates the notification message corresponding to the available assignments.

    :param available_assignments: Number of reviews and lessons that are available.
    :param message_template: Message template where the generated number of reviews and lessons
                                replaces the {} format specifier
    :return: a string containing the notification message to send if at least one assignment is available,
                None otherwise
    """
    if not sum(available_assignments):
        return

    available_lessons_message = ""
    available_reviews_message = ""
    if available_assignments.lessons:
        available_lessons_message = f"{available_assignments.lessons} lessons"
    if available_assignments.reviews:
        available_reviews_message = f"{available_assignments.reviews} reviews"

    full_message = " and ".join(m for m in [available_lessons_message, available_reviews_message] if m)
    return message_template.format(full_message) if message_template else full_message
