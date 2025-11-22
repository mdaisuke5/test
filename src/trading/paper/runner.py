from __future__ import annotations

import argparse
import csv
from datetime import datetime
from pathlib import Path
from typing import List

from trading.backtest.engine import run_backtest_from_dataframe
from trading.config.loader import load_config
from trading.utils.logging import setup_logging


Bar = dict


def load_tick_replay(start: str, end: str) -> List[Bar]:
    path = Path("./data/tick/ticks.csv")
    if not path.exists():
        raise FileNotFoundError("Tick replay data missing at ./data/tick/ticks.csv")
    bars: List[Bar] = []
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
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    args = parser.parse_args()

    setup_logging()
    cfg = load_config(args.config)
    df = load_tick_replay(args.start, args.end)
    metrics = run_backtest_from_dataframe(df, cfg)
    print(metrics)


if __name__ == "__main__":
    main()
