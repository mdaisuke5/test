# Trading System Skeleton

This repository provides a basic structure for a trading system with separate modules for core functionality and machine learning components. The project is organized to support backtesting, paper trading, and live trading via simple shell scripts.

## Setup

1. Clone the repository and navigate into the project directory.
2. Create a Python virtual environment and install your dependencies.
3. Copy `.env.sample` to `.env` and fill in your API keys.

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt  # if you have a requirements file
cp .env.sample .env
```

## Running

Use the scripts in the `scripts/` directory to run different modes of the system:

```bash
./scripts/run_backtest.sh   # run a historical backtest
./scripts/run_paper.sh      # run paper trading
./scripts/run_live.sh       # run live trading
```

The scripts simply call `python -m app.main` with the appropriate mode. Implement `app/main.py` to tie everything together.

## Configuration

YAML configuration files reside in the `configs/` directory:

- `core.yaml` defines the broker and strategy options.
- `ml.yaml` lists the machine learning modules.
- `paths.yaml` sets base directories for data, logs, and models.

Adjust these files according to your environment and strategy parameters.

## Architecture Overview

```
├── app/          # entry points and orchestration
├── core/         # broker abstractions and trading strategies
├── ml/           # machine learning modules
├── pipelines/    # data and execution pipelines
├── utils/        # utility functions
├── configs/      # YAML configuration files
├── scripts/      # helper scripts for running the system
└── data/         # dataset directory (ignored by Git)
```

- **Broker abstraction**: Located under `core/broker.py`, it defines a base `Broker` interface and a simple in-memory `PaperBroker`.
- **Rule-based strategy**: Implemented in `core/strategy.py`, this demonstrates how to create trading signals from predefined rules.
- **Machine learning modules**: Each module under `ml/` is a placeholder for more sophisticated models such as `AlphaModel`, `RegimeClassifier`, `Sizer`, `CostPredictor`, `AutoTuner`, and `AnomalyDetector`.

This structure is intended to be a starting point—you can extend each module with real implementations and add tests as your project evolves.
