from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class OrderRequest:
    symbol: str
    side: str
    size: int
    price: Optional[float] = None
    tif: str = "FAS"


@dataclass
class OrderResponse:
    order_id: str
    status: str
    details: Dict[str, str]


class BrokerInterface(abc.ABC):
    @abc.abstractmethod
    def send_order(self, request: OrderRequest) -> OrderResponse:
        ...

    @abc.abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        ...

    @abc.abstractmethod
    def refresh_token(self) -> None:
        ...
