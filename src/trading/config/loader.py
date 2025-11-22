from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

try:  # pragma: no cover
    import yaml
except Exception:  # pragma: no cover - fallback parser
    yaml = None


def _coerce(value: str) -> Any:
    if value.lower() in {"true", "yes"}:
        return True
    if value.lower() in {"false", "no"}:
        return False
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def _simple_yaml(text: str) -> Dict[str, Any]:
    root: Dict[str, Any] = {}
    stack = [(root, 0)]
    for line in text.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        key, _, val = line.strip().partition(":")
        val = val.strip()
        while stack and indent < stack[-1][1]:
            stack.pop()
        current = stack[-1][0]
        if val == "":
            current[key] = {}
            stack.append((current[key], indent + 2))
        else:
            current[key] = _coerce(val)
    return root


@dataclass
class WalkForwardConfig:
    start: dt.date
    end: dt.date
    step_months: int


@dataclass
class PaperConfig:
    start: dt.date
    end: dt.date


@dataclass
class StrategyParams:
    ema_fast: int
    ema_slow: int
    vwap_sigma: float
    adx_period: int
    adx_threshold: float
    atr_period: int
    tp_mult: float
    sl_mult: float
    ema_slope_period: int
    ema_slope_tf: str


@dataclass
class RiskConfig:
    per_trade_pct: float
    max_intraday_dd: float
    throttle_hour: int
    throttle_day: int
    kelly: bool = False


@dataclass
class ExecutionConfig:
    tick_value: float
    contract: str


@dataclass
class StrategyConfig:
    session: str
    walkforward: WalkForwardConfig
    paper: PaperConfig
    params: StrategyParams
    risk: RiskConfig
    execution: ExecutionConfig


def _as_date(value: Any) -> dt.date:
    if isinstance(value, dt.date):
        return value
    return dt.datetime.strptime(str(value), "%Y-%m-%d").date()


def load_config(path: str | Path) -> StrategyConfig:
    text = Path(path).read_text()
    if yaml:
        raw: Dict[str, Any] = yaml.safe_load(text)
    else:
        raw = _simple_yaml(text)

    walk = raw.get("walkforward", {})
    paper = raw.get("paper", {})
    params = raw.get("params", {})
    risk = raw.get("risk", {})
    execution = raw.get("execution", {})

    return StrategyConfig(
        session=raw.get("session", "day"),
        walkforward=WalkForwardConfig(
            start=_as_date(walk.get("start")),
            end=_as_date(walk.get("end")),
            step_months=int(walk.get("step_months", 6)),
        ),
        paper=PaperConfig(
            start=_as_date(paper.get("start")),
            end=_as_date(paper.get("end")),
        ),
        params=StrategyParams(
            ema_fast=int(params.get("ema_fast", 12)),
            ema_slow=int(params.get("ema_slow", 36)),
            vwap_sigma=float(params.get("vwap_sigma", 0.2)),
            adx_period=int(params.get("adx_period", 14)),
            adx_threshold=float(params.get("adx_threshold", 25)),
            atr_period=int(params.get("atr_period", 14)),
            tp_mult=float(params.get("tp_mult", 4)),
            sl_mult=float(params.get("sl_mult", 1)),
            ema_slope_period=int(params.get("ema_slope_period", 55)),
            ema_slope_tf=str(params.get("ema_slope_tf", "5m")),
        ),
        risk=RiskConfig(
            per_trade_pct=float(risk.get("per_trade_pct", 0.002)),
            max_intraday_dd=float(risk.get("max_intraday_dd", 0.02)),
            throttle_hour=int(risk.get("throttle_hour", 6)),
            throttle_day=int(risk.get("throttle_day", 20)),
            kelly=bool(risk.get("kelly", False)),
        ),
        execution=ExecutionConfig(
            tick_value=float(execution.get("tick_value", 100)),
            contract=str(execution.get("contract", "nikkei225mini")),
        ),
    )


__all__ = [
    "load_config",
    "StrategyConfig",
    "StrategyParams",
    "RiskConfig",
    "ExecutionConfig",
    "WalkForwardConfig",
    "PaperConfig",
]
