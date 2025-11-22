#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH=./src
poetry run python -m trading.backtest.cli --config config/strategy.yml
