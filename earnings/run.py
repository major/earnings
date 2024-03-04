"""Execution part of the package"""

import logging
import os
import sys

import requests
from discord_webhook import DiscordWebhook

from earnings.report import Report

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
log = logging.getLogger(__name__)

# The Discord webhook URL where messages should be sent. For threads, append
# ?thread_id=1234567890 to the end of the URL.
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "LOL NOPE")


def send_message(discord_messages: list) -> requests.Response:
    """Publish a Discord message based on the earnings report."""
    webhook = DiscordWebhook(
        url=WEBHOOK_URL,
        username="EarningsBot",
        rate_limit_retry=True,
        content=f"```{'\n'.join(discord_messages)}```",
    )
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

    # Set up a list to hold discord messages starting with a header.
    discord_messages = []

    # Process the queue.
    for message in queue:
        report = Report(message)

        # If the earnings data or consensus data is missing, skip the report. This is
        # likely a company we aren't interested in.
        if "not found" in report.title:
            continue

        logging.info("Processing %s...", report.ticker)
        discord_messages.append(report.title)

    if len(discord_messages) > 0:
        send_message(discord_messages)

    last_message = max([x["id"] for x in queue])

    # Save the last message ID to a file.
    with open("last_message_id.txt", "w", encoding="utf8") as f:
        f.write(str(last_message) + "\n")
