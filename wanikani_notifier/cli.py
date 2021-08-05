from collections import namedtuple
from datetime import datetime, timedelta
from functools import update_wrapper
from typing import Optional, Generator, Any, Callable, Tuple, List

import click

from wanikani_api.client import Client as WaniKaniClient
from wanikani_notifier.notifiers import notifier
from wanikani_notifier.notifiers.notifier import Notifier
from wanikani_notifier.notifiers.console import ConsoleNotifier
from wanikani_notifier.notifiers.pushover import PushoverNotifier
from wanikani_notifier.notifiers.pushsafer import PushSaferNotifier
from wanikani_notifier.wanikani import get_notification_message, get_available_assignments


def processor(f: Callable):
    def new_func(*args, **kwargs):
        def processor(context: Context, message_stream: Generator[str, Any, None]):
            return f(context, message_stream, *args, **kwargs)

        return processor

    return update_wrapper(new_func, f)


def generator(f: Callable):
    @processor
    def new_func(context: Context, message_stream: str, *args, **kwargs) -> Generator[str, Any, None]:
        yield from message_stream
        yield from f(context, *args, **kwargs)

    return update_wrapper(new_func, f)


@click.group(chain=True)
@click.option("--wanikani", required=True, help="WaniKani API token")
@click.option("--stop-if-empty/--continue-even-empty",
              default=True,
              help="Determines whether chaining occurs when one command does not trigger a new message to notify"
              )
def cli(wanikani: str, stop_if_empty: bool):
    pass  # pragma: nocover


Context = namedtuple("Context", ("wanikani_client", "stop_if_empty"))


@cli.resultcallback()
def process_all(processors, wanikani: str, stop_if_empty: bool):
    context = Context(wanikani_client=WaniKaniClient(wanikani), stop_if_empty=stop_if_empty)

    message_stream = ()
    for processor in processors:
        message_stream = processor(context, message_stream)

    for _ in message_stream:
        pass


@cli.command("available_assignments_now")
@click.option(
    "--since",
    required=False,
    default=-1,
    help="How many hours since assignments are accounted for (-1 meaning forever)",
    show_default=True
)
@click.option(
    "--min",
    "min_assignments",
    required=False,
    type=click.IntRange(min=1),
    default=1,
    help="Minimum number of assignments to generate a message",
    show_default=True
)
@generator
def cli_available_assignments_now(context: Context, since: int, min_assignments: int):
    yield available_assignments_now(context.wanikani_client, since, min_assignments)


def available_assignments_now(wanikani_client: WaniKaniClient, since: int, min_assignments: int):
    current_time_rounded = datetime.utcnow()
    start_time = (current_time_rounded - (timedelta(hours=since) - timedelta(seconds=1)) if since >= 0 else None)
    assignments_available_now = get_available_assignments(wanikani_client,
                                                          start=start_time,
                                                          end=current_time_rounded
                                                          )
    if sum(assignments_available_now) >= min_assignments:
        return get_notification_message(assignments_available_now, message_template="{} are now available!")
    else:
        return


@cli.command("all_available_assignments")
@generator
def cli_all_available_assignments(context: Context):
    yield all_available_assignments(context.wanikani_client)


def all_available_assignments(wanikani_client: WaniKaniClient):
    current_time_rounded = datetime.utcnow()
    all_assignments_available = get_available_assignments(wanikani_client, end=current_time_rounded)
    return get_notification_message(all_assignments_available, message_template="In total, there are {} to do.")


@cli.command("notify")
@click.option("--console/--no-console", required=False, help="Activates notifications though the console")
@click.option("--pushsafer",
              required=False,
              help="Activates notifications though PushSafer by providing the private key"
              )
@click.option("--pushover",
              nargs=2,
              type=str,
              required=False,
              help="Activates notifications though Pushover by providing the app key and the user key"
              )
@processor
def cli_notify(context: Context,
               message_stream: Generator[str, Any, None],
               pushsafer: Optional[str],
               pushover: Optional[Tuple[str, str]],
               console: Optional[bool]
               ) -> None:
    notifiers = []
    if pushsafer:
        notifiers.append(notifier.factory.create(PushSaferNotifier.key(), private_key=pushsafer))
    if pushover:
        notifiers.append(notifier.factory.create(PushoverNotifier.key(), app_token=pushover[0], user_token=pushover[1]))
    if console:
        notifiers.append(notifier.factory.create(ConsoleNotifier.key()))

    messages = list(message_stream)
    if context.stop_if_empty and not all(messages):
        yield
        return

    notify("\n".join(m for m in messages if m), notifiers)
    yield


def notify(message: str, notifiers: List[Notifier]) -> None:
    if message:
        for n in notifiers:
            n.notify(title="WaniKani", message=message, url="https://www.wanikani.com/dashboard")
