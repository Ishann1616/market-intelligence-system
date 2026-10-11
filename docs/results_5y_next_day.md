# 5-year results (next-day execution, after the lookahead fix)

Same window and costs as results_5y_same_day.md. Signals are executed at the next trading day's close.
Buy & Hold is identical to the earlier run, which confirms the fix only affected the strategies.

## Sharpe ratio

| Ticker | Buy & Hold | Momentum | Mean-Reversion |
|---|---|---|---|
| AAPL | 0.694 | 0.458 | 0.687 |
| TSLA | 0.333 | 0.068 | 0.513 |
| JPM | 0.874 | 0.585 | 0.563 |
| KO | 0.845 | 0.384 | 0.738 |
| NVDA | 1.070 | 0.734 | 0.757 |
| MSFT | 0.507 | 0.050 | 0.340 |

## Total return %

| Ticker | Buy & Hold | Momentum | Mean-Reversion |
|---|---|---|---|
| AAPL | 111.21 | 37.65 | 81.57 |
| TSLA | 10.64 | -20.47 | 87.94 |
| JPM | 141.29 | 51.09 | 42.31 |
| KO | 83.69 | 21.14 | 40.27 |
| NVDA | 652.52 | 165.31 | 141.47 |
| MSFT | 64.58 | -2.91 | 26.10 |

Average Sharpe: Buy & Hold 0.72, Mean-Reversion 0.60 (0.70 before the fix), Momentum 0.38 (unchanged).