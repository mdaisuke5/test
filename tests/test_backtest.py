from trading.backtest import run_backtest


def test_backtest_profit_snapshot():
    result = run_backtest()
    assert result == {"profit": 42}
