"""Console script for wanikani_notifier."""

import sys
from typing import Optional

import click

from wanikani_api.client import Client as WaniKaniClient

from wanikani_notifier import wanikani_notifier
from wanikani_notifier.notifiers.console import ConsoleNotifier
from wanikani_notifier.notifiers.pushsafer import PushSaferNotifier


@click.command()
@click.option("--wanikani", required=True, help="WaniKani API token")
@click.option(
    "--since",
    required=False,
    default=-1,
    help="How many hours since assignments are accounted for (-1 meaning forever)",
    show_default=True
)
@click.option("--pushsafer",
              required=False,
              help="Activates notifications though PushSafer by providing the private key"
              )
@click.option("--console/--no-console", required=False, help="Activates notifications though the console")
def main(wanikani: str,
         since: int,
         pushsafer: Optional[str],
         console: Optional[str]
         ) -> int:
    notifiers = []
    if pushsafer:
        notifiers.append(PushSaferNotifier(pushsafer))
    if console:
        notifiers.append(ConsoleNotifier())

    wanikani_notifier.notify_available_assignments(WaniKaniClient(wanikani), since, notifiers)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
