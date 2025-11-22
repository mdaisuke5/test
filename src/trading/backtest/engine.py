from __future__ import annotations

import math
from collections import deque
from statistics import mean, pstdev
from typing import Callable, Dict, List, Sequence

from trading.config.loader import StrategyConfig
from trading.utils.logging import logger

Bar = Dict[str, float | int | object]


def _ema(values: Sequence[float], period: int) -> List[float]:
    result: List[float] = []
    k = 2 / (period + 1)
    for v in values:
        if not result:
            result.append(v)
        else:
            result.append(v * k + result[-1] * (1 - k))
    return result


def _rolling_mean(vals: deque[float]) -> float:
    return mean(vals) if vals else 0.0


def _rolling_std(vals: deque[float]) -> float:
    return pstdev(vals) if len(vals) > 1 else 0.0


def _calc_adx(highs: List[float], lows: List[float], closes: List[float], period: int) -> List[float]:
    adx: List[float] = []
    plus_dm_list: List[float] = []
    minus_dm_list: List[float] = []
    atr_list: List[float] = []
    tr_vals: deque[float] = deque(maxlen=period)
    plus_vals: deque[float] = deque(maxlen=period)
    minus_vals: deque[float] = deque(maxlen=period)

    for i in range(len(highs)):
        if i == 0:
            plus_dm = minus_dm = tr = 0.0
        else:
            up_move = highs[i] - highs[i - 1]
            down_move = lows[i - 1] - lows[i]
            plus_dm = up_move if up_move > down_move and up_move > 0 else 0.0
            minus_dm = down_move if down_move > up_move and down_move > 0 else 0.0
            tr = max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1]))
        tr_vals.append(tr)
        plus_vals.append(plus_dm)
        minus_vals.append(minus_dm)

        atr = _rolling_mean(tr_vals)
        plus_di = 100 * (_rolling_mean(plus_vals) / atr) if atr else 0.0
        minus_di = 100 * (_rolling_mean(minus_vals) / atr) if atr else 0.0
        if plus_di + minus_di == 0:
            adx.append(0.0)
            continue
        dx = abs(plus_di - minus_di) / (plus_di + minus_di) * 100
        adx.append(dx)

    smoothed: List[float] = []
    for i, dx in enumerate(adx):
        if i < period:
            smoothed.append(mean(adx[: i + 1]))
        else:
            smoothed.append((smoothed[-1] * (period - 1) + dx) / period)
    return smoothed


def _manual_backtest(bars: List[Bar], cfg: StrategyConfig) -> Dict[str, float]:
    params = cfg.params
    risk = cfg.risk
    exec_cfg = cfg.execution

    closes = [float(b["close"]) for b in bars]
    highs = [float(b["high"]) for b in bars]
    lows = [float(b["low"]) for b in bars]
    volumes = [float(b.get("volume", 1)) for b in bars]
    times = [b.get("datetime") for b in bars]

    ema_fast = _ema(closes, params.ema_fast)
    ema_slow = _ema(closes, params.ema_slow)
    ema_slope = [0.0] + [ema_slow[i] - ema_slow[i - 1] for i in range(1, len(ema_slow))]

    vwap_vals: List[float] = []
    vwap_std_vals: List[float] = []
    typical_window: deque[float] = deque(maxlen=params.ema_slow)
    volume_window: deque[float] = deque(maxlen=params.ema_slow)

    for i in range(len(bars)):
        typical = (highs[i] + lows[i] + closes[i]) / 3
        typical_window.append(typical)
        volume_window.append(volumes[i])
        weighted_sum = sum(t * v for t, v in zip(typical_window, volume_window))
        volume_sum = sum(volume_window) or 1
        vwap_vals.append(weighted_sum / volume_sum)
        vwap_std_vals.append(_rolling_std(typical_window))

    atr_window: deque[float] = deque(maxlen=params.atr_period)
    atr_vals: List[float] = []
    for i in range(len(bars)):
        atr_window.append(highs[i] - lows[i])
        atr_vals.append(_rolling_mean(atr_window))

    adx_vals = _calc_adx(highs, lows, closes, params.adx_period)

    equity = 10_000_000.0
    peak = equity
    position = 0
    entry = 0.0
    trade_count = 0
    wins = 0
    pnl = 0.0
    returns: List[float] = []
    trade_times: List = []

    for i, bar in enumerate(bars):
        ts = times[i]
        recent_hour = [t for t in trade_times if (ts - t).total_seconds() <= 3600] if ts else []
        recent_day = [t for t in trade_times if t.date() == ts.date()] if ts else []
        if position == 0 and (len(recent_hour) >= risk.throttle_hour or len(recent_day) >= risk.throttle_day):
            continue

        peak = max(peak, equity)
        if peak and (equity - peak) / peak <= -risk.max_intraday_dd:
            position = 0
            entry = 0
            continue

        if position == 0:
            signal = (
                ema_fast[i] > ema_slow[i]
                and closes[i] > vwap_vals[i] + params.vwap_sigma * vwap_std_vals[i]
                and adx_vals[i] > params.adx_threshold
                and ema_slope[i] > 0
            )
            if signal:
                atr = max(atr_vals[i], 1)
                risk_per_contract = atr * exec_cfg.tick_value
                size = max(1, int(equity * risk.per_trade_pct / risk_per_contract))
                position = size
                entry = closes[i]
                if ts:
                    trade_times.append(ts)
        else:
            atr = max(atr_vals[i], 1)
            tp = entry + atr * params.tp_mult
            sl = entry - atr * params.sl_mult
            exit_price = None
            if highs[i] >= tp:
                exit_price = tp
            elif lows[i] <= sl:
                exit_price = sl
            if exit_price is not None:
                trade_count += 1
                trade_pnl = (exit_price - entry) * position * exec_cfg.tick_value
                pnl += trade_pnl
                equity += trade_pnl
                wins += 1 if trade_pnl > 0 else 0
                returns.append(trade_pnl / 10_000_000.0)
                position = 0
                entry = 0

    win_rate = wins / trade_count if trade_count else 0.0
    sharpe = (mean(returns) / pstdev(returns) * math.sqrt(252)) if len(returns) > 1 and pstdev(returns) else 0.0
    dd = abs((equity - peak) / peak) * 100 if peak else 0.0
    q_stat = 1.0

    return dict(pnl=pnl, sharpe=sharpe, max_dd=dd, win_rate=win_rate, trade_count=trade_count, q_stat=q_stat)


def run_backtest_from_dataframe(df: List[Bar], cfg: StrategyConfig) -> Dict[str, float]:
    logger.info("backtest_manual_mode")
    return _manual_backtest(df, cfg)


def walkforward_backtest(cfg: StrategyConfig, df_loader: Callable) -> List[Dict[str, float]]:
    results = []
    current_start = cfg.walkforward.start
    end = cfg.walkforward.end
    step_months = cfg.walkforward.step_months
    while current_start < end:
        # naive month step
        month = (current_start.month - 1 + step_months) % 12 + 1
        year = current_start.year + ((current_start.month - 1 + step_months) // 12)
        day = min(current_start.day, 28)
        next_date = current_start.replace(year=year, month=month, day=day)
        segment_end = end if next_date > end else next_date
        segment_df = df_loader(current_start, segment_end)
        metrics = run_backtest_from_dataframe(segment_df, cfg)
        metrics["start"] = current_start.isoformat()
        metrics["end"] = segment_end.isoformat()
        results.append(metrics)
        current_start = segment_end
    return results


__all__ = ["run_backtest_from_dataframe", "walkforward_backtest"]
