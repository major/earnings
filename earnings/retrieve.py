"""Build a queue of earnings reports to be processed."""

import logging
import sys
from operator import itemgetter

import requests

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)


def get_page(max_message_id=None):
    """Get a page of earnings results from StockTwits.

    Args:
        max_message_id (_type_, optional): Highest message ID to find. Defaults to None.

    Returns:
        list: List of messages from StockTwits.
    """
    stocktwits_url = "https://api.stocktwits.com/api/2/streams/user/epsguid.json"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0"
    }

    params = {"filter": "all", "limit": 49}

    if max_message_id:
        params["max"] = max_message_id

    logging.info("Getting latest messages...")
    resp = requests.get(stocktwits_url, params=params, headers=headers, timeout=30)

    # Sort the messages newest first.
    return sorted(resp.json()["messages"], key=itemgetter("id"), reverse=True)


def build_queue(last_message_id=None):
    """Build a queue of messages to process.

    Args:
        last_message_id (_type_, optional): Highest message ID to find. Defaults to None.

    Returns:
        list: List of messages from StockTwits.
    """
    logging.info("Building queue...")

    # If we don't have a last_message_id, get one page and return that.
    if not last_message_id:
        return get_page()

    queue = []
    starting_message_id = None

    # Loop through multiple pages until we see our last message ID.
    while True:
        messages = get_page(starting_message_id)

        # Add each message to the queue until we see a previously seen one.
        for message in messages:
            if message["id"] == last_message_id or message["id"] < last_message_id:
                return queue
            queue.append(message)

        # The lowest numbered message in queue is our new starting point to get the next
        # page.
        starting_message_id = min([x["id"] for x in queue])

    return queue
