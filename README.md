# Nikkei-225 Futures Automated Trading System

Production-ready skeleton for a systematic trading stack targeting Nikkei-225 mini futures on Osaka Exchange. It includes walk-forward backtests on minute bars, tick-based paper trading, and live connectivity to the kabuステーション® API.

## Features
- Backtrader-based strategy with EMA crossover, VWAP filter, ADX trend strength, ATR-based TP/SL, and slope filter.
- Risk controls: per-trade risk budget, intraday drawdown kill-switch, trade throttling, and Kelly sizing toggle.
- Broker abstraction with rate-limited kabu.com adapter, Redis Streams publishing, and token refresh around maintenance window.
- Docker Compose stack with Redis + monitoring, structlog JSON logging, Slack alert hooks.
- Walk-forward and paper-test runners plus baseline pytest expectation.

See `reports/walkforward_report.md` for summary results and `config/strategy.yml` for tunable parameters.
