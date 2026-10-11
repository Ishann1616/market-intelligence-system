# 5-year results (same-day execution, before the lookahead fix)

Window: Dec 2021 to Sept 2026. $10,000 start, 0.1% cost per trade.
Trades were executed at the same close that produced the signal (optimistic). Kept to compare against the fixed version.

## Sharpe ratio

| Ticker | Buy & Hold | Momentum | Mean-Reversion |
|---|---|---|---|
| AAPL | 0.694 | 0.311 | 0.709 |
| TSLA | 0.333 | 0.250 | 0.641 |
| JPM | 0.874 | 0.520 | 0.875 |
| KO | 0.845 | 0.483 | 0.799 |
| NVDA | 1.070 | 0.857 | 0.889 |
| MSFT | 0.507 | -0.125 | 0.299 |

## Total return %

| Ticker | Buy & Hold | Momentum | Mean-Reversion |
|---|---|---|---|
| AAPL | 111.21 | 20.86 | 84.64 |
| TSLA | 10.64 | 11.54 | 148.74 |
| JPM | 141.29 | 43.16 | 76.94 |
| KO | 83.69 | 28.88 | 44.29 |
| NVDA | 652.52 | 229.27 | 198.52 |
| MSFT | 64.58 | -15.42 | 21.17 |

## Bootstrap vs buy-and-hold: all 12 comparisons inconclusive (10-day blocks, 5,000 iterations, seed 42)