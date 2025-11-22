# Walk-forward & Paper Test Summary

| Period | PnL (JPY) | Sharpe | Max DD (%) | Win % | Trades | Avg Slippage (ticks) | Q-stat p-value |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2019-01-01 to 2019-06-30 | 320000 | 1.35 | -1.2 | 0.58 | 42 | 1.2 | 0.42 |
| 2019-07-01 to 2019-12-31 | 410000 | 1.44 | -1.0 | 0.60 | 39 | 1.1 | 0.39 |
| ... | ... | ... | ... | ... | ... | ... | ... |
| 2024-07-01 to 2024-12-31 | 280000 | 1.28 | -1.6 | 0.55 | 37 | 1.0 | 0.40 |
| **Tick paper 2025-01-01 to 2025-05-31** | **150000** | **1.22** | **-1.4** | **0.54** | **28** | **1.3** | **0.47** |

**Notes**
- Metrics computed on 1-minute walk-forward windows (6-month step) and tick-replay paper test.
- Slippage assumes 1–2 tick impact; adjust via execution simulator as needed.
- Deployment gate: Sharpe ≥ 1.2 and intraday DD within -2.0% satisfied in the aggregated results above.
