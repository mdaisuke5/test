class RiskGuard:
    """Simple risk guard checking drawdown."""

    def __init__(self, max_drawdown: float) -> None:
        self.max_drawdown = max_drawdown

    def check(self, drawdown: float) -> bool:
        """Return True if drawdown is within allowed limits."""
        return drawdown < self.max_drawdown
