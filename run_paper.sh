#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH=./src
poetry run python -m trading.paper.runner --config config/strategy.yml --start 2025-01-01 --end 2025-05-31
