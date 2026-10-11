# 10-year results (next-day execution)

Window: about 10 years, starting about 50 trading days after the data begins (indicator warmup). $10,000 start, 0.1% cost per trade, signals executed at the next day's close.

## Sharpe ratio

| Ticker | Buy & Hold | Momentum | Mean-Reversion |
|---|---|---|---|
| AAPL | 1.029 | 0.858 | 0.567 |
| TSLA | 0.869 | 0.607 | 0.370 |
| JPM | 0.741 | 0.653 | 0.513 |
| KO | 0.673 | 0.280 | 0.797 |
| NVDA | 1.183 | 0.903 | 0.626 |
| MSFT | 0.961 | 0.451 | 0.440 |
| **Average** | **0.91** | **0.63** | **0.55** |

## Total return %

| Ticker | Buy & Hold | Momentum | Mean-Reversion |
|---|---|---|---|
| AAPL | 1155.61 | 367.51 | 159.78 |
| TSLA | 2731.60 | 429.07 | 94.77 |
| JPM | 405.77 | 170.61 | 127.22 |
| KO | 185.68 | 33.96 | 147.33 |
| NVDA | 9082.20 | 1261.61 | 272.99 |
| MSFT | 840.80 | 97.31 | 94.19 |

## Bootstrap vs buy-and-hold (10-day blocks, 5,000 iterations, seed 42)

| Ticker | Strategy | Sharpe | Diff vs B&H | Diff 95% CI | Verdict |
|---|---|---|---|---|---|
| AAPL | Momentum | 0.858 | -0.172 | (-0.63, 0.26) | inconclusive |
| AAPL | Mean-Reversion | 0.567 | -0.463 | (-0.93, 0.03) | inconclusive |
| TSLA | Momentum | 0.607 | -0.262 | (-0.71, 0.2) | inconclusive |
| TSLA | Mean-Reversion | 0.370 | -0.499 | (-0.97, 0.01) | inconclusive |
| JPM | Momentum | 0.653 | -0.088 | (-0.61, 0.43) | inconclusive |
| JPM | Mean-Reversion | 0.513 | -0.228 | (-0.63, 0.22) | inconclusive |
| KO | Momentum | 0.280 | -0.394 | (-0.77, 0.01) | inconclusive |
| KO | Mean-Reversion | 0.797 | 0.123 | (-0.35, 0.67) | inconclusive |
| NVDA | Momentum | 0.903 | -0.280 | (-0.7, 0.15) | inconclusive |
| NVDA | Mean-Reversion | 0.626 | -0.558 | (-1.07, 0.02) | inconclusive |
| MSFT | Momentum | 0.451 | -0.510 | (-0.92, -0.11) | WORSE |
| MSFT | Mean-Reversion | 0.440 | -0.521 | (-0.97, -0.06) | WORSE |

## Compared with the 5-year window (same execution rule)

Average Sharpe: Buy & Hold 0.72 to 0.91, Momentum 0.38 to 0.63, Mean-Reversion 0.60 to 0.55.
Mean-reversion looked best over 5 years and worst over 10. Which agent looks better depends on the window.
