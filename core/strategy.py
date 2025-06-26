from typing import Any, List


class RuleBasedStrategy:
    """Simple rule-based trading strategy."""

    def __init__(self, rules: List[Any]) -> None:
        self.rules = rules

    def generate_signals(self, data: Any) -> List[Any]:
        """Generate trading signals based on predefined rules."""
        signals = []
        for rule in self.rules:
            if rule(data):
                signals.append({"action": "BUY", "symbol": data.get("symbol"), "qty": 1})
        return signals
