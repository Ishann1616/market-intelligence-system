# Assumptions & Shortcuts Log

Every assumption or simplification made while building, and how it could affect results.

## Data
- Test stocks: AAPL, TSLA, JPM, KO, NVDA, MSFT (5 years of daily data via yfinance)
- All 6 test stocks are large-cap US survivors that moved together in a bull market, so they are not 6 independent tests

## Backtest
- Trades cost 0.1% each (fees + slippage combined), a rough estimate
- Strategies are all-in or all-out: 100% stock or 100% cash, no partial positions
- Cash earns 0% while out of the market (slightly penalizes both strategies)
- All strategies start on 2021-12-06, the latest warmup end, so the comparison is fair

## Metrics
- Sharpe ratio uses a risk-free rate of 0 (makes Sharpe look slightly better than reality)
- Bootstrap significance test: 10-day block resampling, 5,000 iterations, seed 42, paired against buy-and-hold. All 12 strategy/ticker comparisons came back inconclusive; ~5 years of data can't resolve Sharpe differences smaller than about ±0.7

## Known limitations
- Results so far come from one stock (AAPL) in one regime (a long uptrend), so they don't generalize yet
- Lower volatility and shallower drawdowns for both strategies are partly mechanical (time spent in cash), not proof of skill

