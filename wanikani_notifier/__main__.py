"""Console script for wanikani_notifier."""

import sys
from typing import Optional

import click

from wanikani_api.client import Client as WaniKaniClient

from wanikani_notifier import wanikani_notifier
from wanikani_notifier.notifiers.pushsafer import PushSaferNotifier


@click.command()
@click.option("--wanikani", required=True, help="WaniKani API token")
@click.option(
    "--since",
    required=False,
    default=-1,
    help="How many hours since assignments are accounted for, defaults to -1 (forever)",
    show_default=True
)
@click.option("--pushsafer", required=False, help="PushSafer private key")
def main(wanikani: str, since: int, pushsafer: Optional[str]) -> int:
    notifiers = []
    if pushsafer:
        notifiers.append(PushSaferNotifier(pushsafer))

    wanikani_notifier.notify_available_assignments(WaniKaniClient(wanikani), since, notifiers)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
