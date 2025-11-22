#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH=./src
poetry run python -m trading.live.runner --config config/strategy.yml
