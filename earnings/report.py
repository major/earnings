"""Object for the earnings report."""

import functools
import re
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class Report:
    """Object for the earnings report."""

    message: dict

    @functools.cached_property
    def body(self) -> str:
        """Get the body of the message."""
        return str(self.message["body"])

    @functools.cached_property
    def consensus(self) -> Optional[int]:
        """Return analyst consensus."""
        regex = r"consensus was \(*\$?([0-9.]+)\)*"
        result = re.search(regex, self.body)

        # Some earnings reports for smaller stocks don't have a consensus.
        if not result:
            return None

        consensus = result.group(1)
        # Check if the original string had parentheses, indicating a loss.
        if "(" in result.group(0):
            return int(float(f"-{consensus}") * 100)

        return int(float(consensus) * 100)

    @functools.cached_property
    def earnings(self) -> Optional[int]:
        """Return the earnings."""
        regex = r"reported (?:earnings of )?\$([0-9\.]+)|(?:a loss of )?\$([0-9\.]+)"
        result = re.search(regex, self.body)

        if result:
            # Check which group was matched to determine if it's a loss or gain.
            earnings, loss = result.groups()
            if loss:
                return int(float(f"-{loss}") * 100)
            elif earnings:
                return int(float(earnings) * 100)

        return None

    @functools.cached_property
    def symbol(self) -> Dict[str, str]:
        """Return the symbol dict of the company."""
        default = {
            "symbol": "N/A",
            "title": "Unknown",
        }

        symbols = self.message.get("symbols", [default])
        symbol = symbols[0]

        return dict(symbol)

    @property
    def name(self) -> str:
        """Return the name of the company."""
        return self.symbol["title"]

    @property
    def ticker(self) -> str:
        """Return the ticker symbol."""
        return self.symbol["symbol"]

    @property
    def winner(self) -> Optional[bool]:
        """Return the winner of the earnings report."""
        if self.consensus is None or self.earnings is None:
            return None

        if self.earnings > self.consensus:
            return True

        return False

    @property
    def color(self) -> str:
        """Return a color for the Discord message."""
        if self.winner is None:
            return "aaaaaa"

        if self.winner:
            return "008000"

        return "d42020"

    @property
    def logo(self) -> str:
        """Return a URL for the company logo."""
        url_base = "https://s3.amazonaws.com/logos.atom.finance/stocks-and-funds"
        return f"{url_base}/{self.ticker}.png"

    @property
    def title(self) -> str:
        """Generate a title for the Discord message."""
        earnings = "Earnings not found"
        if self.earnings is not None:
            earnings = f"${self.earnings/100:.2f}"

        consensus = "Consensus not found"
        if self.consensus is not None:
            consensus = f"${self.consensus/100:.2f}"

        return f"{self.ticker}: {earnings} vs. {consensus} expected"
