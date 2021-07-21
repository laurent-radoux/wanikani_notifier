"""Console script for wanikani_notifier."""

import sys
import click

from wanikani_notifier import wanikani_notifier


@click.command()
@click.option("-w", "--wanikani-token", required=True, help="WaniKani API token")
@click.option("-p", "--pushsafer-token", required=True, help="PushSafer private key")
def main(wanikani_token: str, pushsafer_token: str) -> int:
    wanikani_notifier.notify_new_assignments(wanikani_token, pushsafer_token)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
