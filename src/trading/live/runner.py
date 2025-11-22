from __future__ import annotations

import argparse
import time

from trading.broker.kabus import KabusAdapter
from trading.config.loader import load_config
from trading.utils.logging import logger, setup_logging


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    setup_logging()
    cfg = load_config(args.config)
    broker = KabusAdapter()
    logger.info("live_loop_start", session=cfg.session)
    try:
        while True:
            broker.refresh_token()
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("live_loop_stop")
    finally:
        broker.stop()


if __name__ == "__main__":
    main()
