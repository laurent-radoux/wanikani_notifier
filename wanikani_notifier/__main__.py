from datetime import datetime, timedelta
from functools import update_wrapper
from typing import Optional, Generator, Any, Callable

import click

from wanikani_api.client import Client as WaniKaniClient

from wanikani_notifier.notifiers import notifier
from wanikani_notifier.notifiers.console import ConsoleNotifier
from wanikani_notifier.notifiers.pushsafer import PushSaferNotifier
from wanikani_notifier.wanikani import get_notification_message, get_available_assignments


def processor(f: Callable):
    def new_func(*args, **kwargs):
        def processor(wanikani_client, message_stream: Generator[str, Any, None]):
            return f(wanikani_client, message_stream, *args, **kwargs)

        return processor

    return update_wrapper(new_func, f)


def generator(f: Callable):
    @processor
    def new_func(wanikani_client, message_stream: str, *args, **kwargs) -> Generator[str, Any, None]:
        yield from message_stream
        yield from f(wanikani_client, *args, **kwargs)

    return update_wrapper(new_func, f)


@click.group(chain=True)
@click.option("--wanikani", required=True, help="WaniKani API token")
def cli(wanikani: str):
    pass


@cli.resultcallback()
def process_all(processors, wanikani: str):
    wanikani_client = WaniKaniClient(wanikani)

    message_stream = ()
    for processor in processors:
        message_stream = processor(wanikani_client, message_stream)

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
@generator
def available_assignments_now(wanikani_client: WaniKaniClient, since: int):
    current_time_rounded = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    start_time = (current_time_rounded - (timedelta(hours=since) - timedelta(seconds=1)) if since >= 0 else None)
    assignments_available_now = get_available_assignments(wanikani_client,
                                                          start=start_time,
                                                          end=current_time_rounded
                                                          )
    yield get_notification_message(assignments_available_now, message_template="{} are now available!")


@cli.command("all_available_assignments")
@generator
def all_available_assignments(wanikani_client: WaniKaniClient):
    current_time_rounded = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    assignments_available_now = get_available_assignments(wanikani_client, end=current_time_rounded)
    yield get_notification_message(assignments_available_now, message_template="In total, there are {} to do.")


@cli.command("notify")
@click.option("--pushsafer",
              required=False,
              help="Activates notifications though PushSafer by providing the private key"
              )
@click.option("--console/--no-console", required=False, help="Activates notifications though the console")
@processor
def notify(wanikani_client: WaniKaniClient,
           message_stream: Generator[str, Any, None],
           pushsafer: Optional[str],
           console: Optional[str]
           ) -> int:
    notifiers = []
    if pushsafer:
        notifiers.append(notifier.factory.create(PushSaferNotifier.key(), private_key=pushsafer))
    if console:
        notifiers.append(notifier.factory.create(ConsoleNotifier.key()))

    messages = list(message_stream)
    final_message = "\n".join(m for m in messages if m)
    if final_message:
        for n in notifiers:
            n.notify("WaniKani", final_message)

    yield from messages


if __name__ == "__main__":
    cli()
