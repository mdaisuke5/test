from __future__ import annotations

import datetime as dt
from typing import Dict, List

try:  # pragma: no cover - optional dependency
    import backtrader as bt
except Exception:  # pragma: no cover - fallback
    class _Placeholder:
        def __init__(self, *args, **kwargs):
            ...

        def __call__(self, *args, **kwargs):
            return self

        def __gt__(self, other):
            return False

        def __lt__(self, other):
            return False

        def __sub__(self, other):
            return 0

        def __add__(self, other):
            return 0

        def __getitem__(self, key):
            return 0

    class bt:  # type: ignore
        class Indicator:
            params = ()
            lines = ()

        class Strategy:
            params = {}

            def __init__(self):
                self.broker = type("Broker", (), {"getvalue": lambda self: 0, "getcash": lambda self: 0})()
                self.position = False

            def buy_bracket(self, *args, **kwargs):
                return None

            def close(self):
                return None

            def cancel(self, o):
                return None

        class Order:
            ...

        class ind:
            EMA = _Placeholder
            CrossOver = _Placeholder
            AverageDirectionalMovementIndex = _Placeholder
            ATR = _Placeholder
            SumN = _Placeholder
            StandardDeviation = _Placeholder


class VWAPStd(bt.Indicator):
    params = ("period",)
    lines = ("vwap", "std")

    def __init__(self):
        typical = (self.data.high + self.data.low + self.data.close) / 3.0
        cum_typical_volume = bt.ind.SumN(typical * self.data.volume, period=self.p.period)
        cum_volume = bt.ind.SumN(self.data.volume, period=self.p.period)
        self.l.vwap = cum_typical_volume / cum_volume
        self.l.std = bt.ind.StandardDeviation(typical, period=self.p.period)


class EmaSlope(bt.Indicator):
    params = ("period",)
    lines = ("slope",)

    def __init__(self):
        ema = bt.ind.EMA(self.data, period=self.p.period)
        self.l.slope = ema - ema(-1)


class TrendStrategy(bt.Strategy):
    params = dict(
        ema_fast=12,
        ema_slow=36,
        vwap_sigma=0.2,
        adx_period=14,
        adx_threshold=25,
        atr_period=14,
        tp_mult=4.0,
        sl_mult=1.0,
        per_trade_pct=0.002,
        tick_value=100,
        slope_period=55,
        throttle_hour=6,
        throttle_day=20,
        kill_dd=0.02,
        kelly=False,
    )

    def __init__(self):
        self.orders: List[bt.Order] = []
        self.ema_fast = bt.ind.EMA(period=self.p.ema_fast)
        self.ema_slow = bt.ind.EMA(period=self.p.ema_slow)
        self.crossover = bt.ind.CrossOver(self.ema_fast, self.ema_slow)
        self.adx = bt.ind.AverageDirectionalMovementIndex(period=self.p.adx_period)
        self.atr = bt.ind.ATR(period=self.p.atr_period)
        self.vwap = VWAPStd(period=36)
        self.slope = EmaSlope(period=self.p.slope_period)
        self.trade_times: List[dt.datetime] = []
        self.start_equity = getattr(self.broker, "getvalue", lambda: 0)()
        self.day_high = self.start_equity

    def nextstart(self):
        self.day_high = getattr(self.broker, "getvalue", lambda: 0)()

    def notify_trade(self, trade):
        if getattr(trade, "justopened", False):
            self.trade_times.append(self.data.datetime.datetime())

    def _throttle_ok(self) -> bool:
        now = self.data.datetime.datetime()
        hour_window = [t for t in self.trade_times if (now - t).total_seconds() <= 3600]
        day_window = [t for t in self.trade_times if t.date() == now.date()]
        return len(hour_window) < self.p.throttle_hour and len(day_window) < self.p.throttle_day

    def _risk_size(self) -> int:
        cash = getattr(self.broker, "getcash", lambda: 0)()
        risk_per_contract = getattr(self.atr, "__getitem__", lambda x: [0])[0] * self.p.tick_value
        risk_budget = cash * self.p.per_trade_pct
        size = max(1, int(risk_budget / max(risk_per_contract, 1)))
        return size

    def _kill_switch(self) -> None:
        equity = getattr(self.broker, "getvalue", lambda: 0)()
        self.day_high = max(self.day_high, equity)
        if self.day_high and (equity - self.day_high) / self.day_high <= -self.p.kill_dd:
            self.close()

    def next(self):
        self._kill_switch()
        if getattr(self, "position", False):
            return
        if not self._throttle_ok():
            return

        long_signal = (
            self.crossover > 0
            and self.data.close[0] > self.vwap.vwap[0] + self.p.vwap_sigma * self.vwap.std[0]
            and self.adx[0] > self.p.adx_threshold
            and self.slope[0] > 0
        )
        if long_signal:
            size = self._risk_size()
            atr = self.atr[0]
            entry = self.data.close[0]
            tp = entry + atr * self.p.tp_mult
            sl = entry - atr * self.p.sl_mult
            self.buy_bracket(size=size, limitprice=tp, stopprice=sl)

    def stop(self):
        for o in self.orders:
            if o and getattr(self, "position", False):
                self.cancel(o)


def build_strategy_kwargs(cfg: StrategyConfig) -> Dict:
    return dict(
        ema_fast=cfg.params.ema_fast,
        ema_slow=cfg.params.ema_slow,
        vwap_sigma=cfg.params.vwap_sigma,
        adx_period=cfg.params.adx_period,
        adx_threshold=cfg.params.adx_threshold,
        atr_period=cfg.params.atr_period,
        tp_mult=cfg.params.tp_mult,
        sl_mult=cfg.params.sl_mult,
        per_trade_pct=cfg.risk.per_trade_pct,
        tick_value=cfg.execution.tick_value,
        slope_period=cfg.params.ema_slope_period,
        throttle_hour=cfg.risk.throttle_hour,
        throttle_day=cfg.risk.throttle_day,
        kill_dd=cfg.risk.max_intraday_dd,
        kelly=cfg.risk.kelly,
    )


__all__ = ["TrendStrategy", "build_strategy_kwargs"]
