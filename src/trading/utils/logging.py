from __future__ import annotations

import logging
import os

try:  # pragma: no cover - optional dependency
    import structlog
except Exception:  # pragma: no cover
    structlog = None


def setup_logging() -> None:
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=getattr(logging, log_level, logging.INFO), format="%(asctime)s %(levelname)s %(message)s")
    if not structlog:
        return
    shared_processors = [
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    structlog.configure(
        processors=[*shared_processors, structlog.processors.JSONRenderer()],
        wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, log_level, logging.INFO)),
        cache_logger_on_first_use=True,
    )


logger = structlog.get_logger() if structlog else logging.getLogger("trading")
