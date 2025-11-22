from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import List

from trading.backtest.engine import run_backtest_from_dataframe, walkforward_backtest
from trading.config.loader import load_config
from trading.utils.logging import setup_logging

Bar = dict


def load_minute_data(start: str, end: str) -> List[Bar]:
    path = Path("./data/min_bar/minute.csv")
    bars: List[Bar] = []
    if not path.exists():
        raise FileNotFoundError("Minute bar data not found in ./data/min_bar/minute.csv")
    with path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            ts = datetime.fromisoformat(row["datetime"])
            if start <= ts.date().isoformat() <= end:
                bars.append(
                    {
                        "datetime": ts,
                        "open": float(row["open"]),
                        "high": float(row["high"]),
                        "low": float(row["low"]),
                        "close": float(row["close"]),
                        "volume": float(row.get("volume", 0)),
                    }
                )
    return bars


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--walkforward", action="store_true", help="Run walk-forward instead of single backtest")
    args = parser.parse_args()

    setup_logging()
    cfg = load_config(args.config)

    if args.walkforward:
        results = walkforward_backtest(cfg, lambda s, e: load_minute_data(s.isoformat(), e.isoformat()))
        print(json.dumps(results, indent=2, default=str))
    else:
        bars = load_minute_data(cfg.walkforward.start.isoformat(), cfg.walkforward.end.isoformat())
        metrics = run_backtest_from_dataframe(bars, cfg)
        print(json.dumps(metrics, indent=2, default=str))


if __name__ == "__main__":
    main()
