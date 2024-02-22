"""Object for the earnings report."""

import re
from dataclasses import dataclass


@dataclass
class Report:
    """Object for the earnings report."""

    message: dict

    @property
    def body(self):
        """Get the body of the message."""
        return self.message["body"]

    @property
    def consensus(self):
        """Return analyst consensus."""
        regex = r"consensus was \(*\$?([0-9.]+)\)*"
        result = re.search(regex, self.body)

        # Some earnings reports for smaller stocks don't have a consensus.
        if not result:
            return None

        consensus = result.group(1)
        # Check if the original string had parentheses, indicating a loss.
        if "(" in result.group(0):
            return float(f"-{consensus}") * 100

        return float(consensus) * 100

    @property
    def earnings(self):
        """Return the earnings."""
        regex = r"reported (?:earnings of )?\$([0-9\.]+)|(?:a loss of )?\$([0-9\.]+)"
        result = re.search(regex, self.body)

        if result:
            # Check which group was matched to determine if it's a loss or gain.
            earnings, loss = result.groups()
            if loss:
                return float(f"-{loss}") * 100
            elif earnings:
                return float(earnings) * 100

        return None

    @property
    def ticker(self):
        """Return the ticker symbol."""
        return self.message["symbols"][0]["symbol"]

    @property
    def winner(self):
        """Return the winner of the earnings report."""
        if not self.consensus:
            return None

        if self.earnings > self.consensus:
            return True

        return False

    @property
    def color(self):
        """Return a color for the Discord message."""
        if self.winner is None:
            return "aaaaaa"

        if self.winner:
            return "008000"

        return "d42020"

    @property
    def logo(self):
        """Return a URL for the company logo."""
        url_base = "https://s3.amazonaws.com/logos.atom.finance/stocks-and-funds"
        return f"{url_base}/{self.ticker}.png"

    @property
    def title(self) -> str:
        """Generate a title for the Discord message."""
        return f"{self.ticker}: ${self.earnings/100:.2f} vs. ${self.consensus/100:.2f} expected"
