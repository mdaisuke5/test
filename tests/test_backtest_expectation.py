import json
import datetime as dt
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from trading.backtest.engine import run_backtest_from_dataframe
from trading.config.loader import StrategyConfig, StrategyParams, WalkForwardConfig, PaperConfig, RiskConfig, ExecutionConfig


def make_dummy_config() -> StrategyConfig:
    return StrategyConfig(
        session="day",
        walkforward=WalkForwardConfig(start=dt.date(2020, 1, 1), end=dt.date(2020, 1, 10), step_months=6),
        paper=PaperConfig(start=dt.date(2025, 1, 1), end=dt.date(2025, 1, 2)),
        params=StrategyParams(
            ema_fast=3,
            ema_slow=6,
            vwap_sigma=0.1,
            adx_period=5,
            adx_threshold=10,
            atr_period=5,
            tp_mult=2.0,
            sl_mult=1.0,
            ema_slope_period=5,
            ema_slope_tf="5m",
        ),
        risk=RiskConfig(per_trade_pct=0.002, max_intraday_dd=0.02, throttle_hour=6, throttle_day=20, kelly=False),
        execution=ExecutionConfig(tick_value=100, contract="mini"),
    )


def make_price_frame():
    bars = []
    start = dt.datetime(2020, 1, 1, 9, 0)
    for i in range(40):
        price = 100 + i
        bars.append(
            {
                "datetime": start + dt.timedelta(minutes=i),
                "open": price + 0.1,
                "high": price + 0.2,
                "low": price - 0.2,
                "close": price,
                "volume": 10,
            }
        )
    return bars


def test_backtest_matches_expectation():
    cfg = make_dummy_config()
    df = make_price_frame()
    metrics = run_backtest_from_dataframe(df, cfg)
    expected = json.loads(Path("tests/fixtures/backtest_expectation.json").read_text())
    for key, value in expected.items():
        assert round(metrics.get(key, 0), 3) == round(value, 3)
