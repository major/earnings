"""Execution part of the package"""

import logging
import os
import sys

import requests
from discord_webhook import DiscordEmbed, DiscordWebhook

from earnings.report import Report

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
log = logging.getLogger(__name__)

# The Discord webhook URL where messages should be sent. For threads, append
# ?thread_id=1234567890 to the end of the URL.
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "LOL NOPE")


def send_message(report: Report) -> requests.Response:
    """Publish a Discord message based on the earnings report."""
    webhook = DiscordWebhook(url=WEBHOOK_URL, username="EarningsBot", rate_limit_retry=True)
    embed = DiscordEmbed(
        title=report.title,
        color=report.color,
    )
    embed.set_author(
        name=report.name,
        url=f"https://finance.yahoo.com/quote/{report.ticker}/",
        icon_url=report.logo,
    )
    webhook.add_embed(embed)
    return webhook.execute()


if __name__ == "__main__":
    from earnings.retrieve import build_queue

    # Get the last message ID from the file.
    with open("last_message_id.txt", encoding="utf8") as fileh:
        last_message_id = int(fileh.read().strip())

    # Build a queue of messages to process.
    queue = build_queue(last_message_id)

    if not queue:
        log.info("No new messages to process.")
        sys.exit(0)

    # Process the queue.
    for message in queue:
        report = Report(message)
        if report.earnings is None:
            continue
        logging.info(f"Processing {report.ticker}...")
        send_message(report)

    last_message = max([x["id"] for x in queue])

    # Save the last message ID to a file.
    with open("last_message_id.txt", "w") as f:
        f.write(str(last_message) + "\n")
