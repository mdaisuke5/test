from __future__ import annotations

import datetime as dt
import os
import queue
import threading
import time
from typing import Any, Dict, Optional

import redis
import requests

from trading.broker.interface import BrokerInterface, OrderRequest, OrderResponse
from trading.utils.logging import logger
from trading.utils.rate_limiter import RateLimiter, RateLimitRule


class KabusAdapter(BrokerInterface):
    def __init__(self, url: Optional[str] = None, redis_host: Optional[str] = None) -> None:
        self.url = url or os.getenv("KABUS_URL", "http://localhost:18080/kabusapi")
        self.token = os.getenv("KABUS_USER_TOKEN", "")
        self.password = os.getenv("KABUS_PASSWORD", "")
        self.redis_client = redis.Redis(host=redis_host or os.getenv("REDIS_HOST", "redis"), port=int(os.getenv("REDIS_PORT", 6379)))
        self.stream = os.getenv("REDIS_STREAM", "fills")
        self._order_q: "queue.Queue[OrderRequest]" = queue.Queue()
        self._stop = threading.Event()
        self._limiter = RateLimiter(RateLimitRule(interval=1.0, max_calls=5))
        self.worker = threading.Thread(target=self._worker, daemon=True)
        self.worker.start()

    def _worker(self) -> None:
        while not self._stop.is_set():
            try:
                req = self._order_q.get(timeout=0.5)
            except queue.Empty:
                continue
            try:
                response = self._send(req)
                self._publish_fill(response)
            except Exception as exc:  # noqa: BLE001
                logger.error("order_failed", error=str(exc))
            finally:
                self._order_q.task_done()

    def _publish_fill(self, response: OrderResponse) -> None:
        payload = {"order_id": response.order_id, "status": response.status, **response.details}
        self.redis_client.xadd(self.stream, payload)

    def _send(self, request: OrderRequest) -> OrderResponse:
        self._limiter.acquire()
        body: Dict[str, Any] = {
            "Password": self.password,
            "Symbol": request.symbol,
            "Exchange": 23,
            "TradeType": 1 if request.side.lower() == "buy" else 2,
            "TimeInForce": request.tif,
            "Qty": request.size,
        }
        if request.price:
            body["Price"] = request.price
        res = requests.post(f"{self.url}/sendorder/future", json=body, headers={"X-API-KEY": self.token}, timeout=5)
        res.raise_for_status()
        data = res.json()
        return OrderResponse(order_id=str(data.get("OrderId", "")), status=str(data.get("ResultCode", "ok")), details=data)

    def send_order(self, request: OrderRequest) -> OrderResponse:
        logger.info("queue_order", symbol=request.symbol, side=request.side, size=request.size)
        self._order_q.put(request)
        return OrderResponse(order_id="queued", status="queued", details={})

    def cancel_order(self, order_id: str) -> bool:
        self._limiter.acquire()
        res = requests.put(f"{self.url}/cancelorder", json={"OrderId": order_id}, headers={"X-API-KEY": self.token}, timeout=5)
        success = res.status_code == 200
        if success:
            logger.info("order_cancelled", order_id=order_id)
        return success

    def refresh_token(self) -> None:
        now = dt.datetime.now(dt.timezone.utc).astimezone(dt.timezone(dt.timedelta(hours=9)))
        if now.hour == 6 and now.minute >= 15:
            res = requests.post(f"{self.url}/token", json={"APIPassword": self.password, "APIKey": os.getenv("KABUS_APP_KEY", "")}, timeout=5)
            if res.status_code == 200:
                self.token = res.json().get("Token", self.token)
                logger.info("token_refreshed")

    def stop(self) -> None:
        self._stop.set()
        self.worker.join(timeout=2)


__all__ = ["KabusAdapter"]
