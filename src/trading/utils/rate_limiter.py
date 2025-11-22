from __future__ import annotations

import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import Callable, Deque, Iterable


@dataclass
class RateLimitRule:
    interval: float
    max_calls: int


class RateLimiter:
    def __init__(self, rule: RateLimitRule) -> None:
        self.rule = rule
        self.timestamps: Deque[float] = deque()
        self.lock = threading.Lock()

    def acquire(self) -> None:
        with self.lock:
            now = time.monotonic()
            while self.timestamps and now - self.timestamps[0] > self.rule.interval:
                self.timestamps.popleft()
            if len(self.timestamps) >= self.rule.max_calls:
                sleep_time = self.rule.interval - (now - self.timestamps[0])
                time.sleep(max(0, sleep_time))
            self.timestamps.append(time.monotonic())

    def wrap(self, func: Callable) -> Callable:
        def wrapped(*args, **kwargs):
            self.acquire()
            return func(*args, **kwargs)

        return wrapped


__all__ = ["RateLimiter", "RateLimitRule"]
