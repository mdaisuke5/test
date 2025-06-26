from abc import ABC, abstractmethod
from typing import Any


class Broker(ABC):
    """Abstract broker interface."""

    @abstractmethod
    def send_order(self, order: Any) -> None:
        """Send an order to the market."""

    @abstractmethod
    def get_positions(self) -> Any:
        """Return current positions."""


class PaperBroker(Broker):
    """Simple in-memory broker for paper trading."""

    def __init__(self) -> None:
        self.orders = []
        self.positions = {}

    def send_order(self, order: Any) -> None:
        self.orders.append(order)
        symbol = order.get("symbol")
        qty = order.get("qty", 0)
        self.positions[symbol] = self.positions.get(symbol, 0) + qty

    def get_positions(self) -> Any:
        return dict(self.positions)
