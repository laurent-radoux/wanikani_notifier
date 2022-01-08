import os
from datetime import datetime
from collections import namedtuple
from typing import Optional, Dict

import pytz
import ujson as ujson
from wanikani_api.client import Client as WaniKaniClient
from wanikani_api.models import Subject

AvailableAssignments = namedtuple("AvailableAssignments", ("reviews", "lessons"))


SUBJECTS_CACHED_FILENAME = "subjects.json"


def get_all_subjects(wk_client: WaniKaniClient) -> Dict[int, Subject]:
    all_subjects: Dict[int, Subject] = {}

    if not os.path.exists("data/"):
        os.makedirs("data/")

    if os.path.exists(f"data/{SUBJECTS_CACHED_FILENAME}"):
        subject_jsons = ujson.load(open(f"data/{SUBJECTS_CACHED_FILENAME}", "r"))
        all_subjects = {subject_json["id"]: Subject(subject_json) for subject_json in subject_jsons}

    latest_update = max([s.data_updated_at for s in all_subjects.values()]) if all_subjects else datetime.min
    for subject in wk_client.subjects(updated_after=latest_update.strftime("%Y-%m-%dT%H:%M:%S.%f"), fetch_all=True):
        all_subjects[subject.id] = subject

    ujson.dump([subject._raw for subject in all_subjects.values()], open(f"data/{SUBJECTS_CACHED_FILENAME}", "w"))

    return all_subjects


def get_available_assignments(wanikani_client: WaniKaniClient,
                              all_subjects: Dict[int, Subject],
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
    user_level = wanikani_client.user_information().level
    review_count = sum(1
                       for a in wanikani_client.assignments(fetch_all=True, unlocked=True, started=True,
                                                            available_after=start, available_before=end)
                       if not a.hidden
                       and a.subject_id in all_subjects and all_subjects[a.subject_id].level <= user_level
                       )
    lesson_count = sum(1
                       for a in wanikani_client.assignments(fetch_all=True, unlocked=True, started=False)
                       if a.created_at.replace(tzinfo=pytz.utc) <= end.replace(tzinfo=pytz.utc)
                       and (start.replace(tzinfo=pytz.utc) <= a.created_at.replace(tzinfo=pytz.utc) if start else True)
                       )

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
