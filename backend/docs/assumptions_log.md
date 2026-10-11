# Assumptions & Shortcuts Log

Every assumption or simplification made while building, and how it could affect results.

## Data
- Test stocks: AAPL, TSLA, JPM, KO, NVDA, MSFT (5 years of daily data via yfinance)

## Backtest
- Trades cost 0.1% each (fees + slippage combined), a rough estimate
- Strategies are all-in or all-out: 100% stock or 100% cash, no partial positions
- Cash earns 0% while out of the market (slightly penalizes both strategies)
- All strategies start on 2021-12-06, the latest warmup end, so the comparison is fair

## Metrics
- Sharpe ratio uses a risk-free rate of 0 (makes Sharpe look slightly better than reality)

## Known limitations
- Results so far come from one stock (AAPL) in one regime (a long uptrend), so they don't generalize yet
