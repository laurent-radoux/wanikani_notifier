"""Console script for wanikani_notifier."""

import sys
import click

from wanikani_notifier import wanikani_notifier


@click.command()
@click.option("-w", "--wanikani-token", required=True, help="WaniKani API token")
@click.option("-p", "--pushsafer-token", required=True, help="PushSafer private key")
@click.option(
    "-h",
    "--hours-ago",
    required=False,
    default=-1,
    help="Period in hours [now-h; now] for which available assignments are queried, defaults to -1 (infinity)",
    show_default=True
)
def main(wanikani_token: str, pushsafer_token: str, hours_ago: int) -> int:
    wanikani_notifier.notify_available_assignments(wanikani_token, pushsafer_token, hours_ago)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
