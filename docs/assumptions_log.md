# Assumptions & Shortcuts Log

Every assumption or simplification made while building, and how it could affect results.

## Data
- Test stocks: AAPL, TSLA, JPM, KO, NVDA, MSFT (daily data via yfinance)
- History window: 10 years (extended from 5 after the first round of results; 5-year results saved in docs/results_5y_same_day.md)
- Prices are yfinance's dividend- and split-adjusted close (default settings); logged closes can differ slightly from raw quoted prices
- All 6 stocks are large-cap US survivors that moved together, so they are not 6 independent tests

## Backtest
- Trades cost 0.1% each (fees + slippage combined), a rough estimate
- Strategies are all-in or all-out: 100% stock or 100% cash, no partial positions
- Cash earns 0% while out of the market (slightly penalizes both strategies)
- All strategies start on the same day, after the longest indicator warmup (50-day MA), so the comparison is fair
- Signals use a day's closing price and are executed at the NEXT trading day's close (one-day delay). Early runs executed at the same close that produced the signal, which was optimistic

## Metrics
- Sharpe ratio uses a risk-free rate of 0 (makes Sharpe look slightly better than reality)
- Bootstrap significance test: 10-day block resampling, 5,000 iterations, seed 42, paired against buy-and-hold

## Forward signal log
- Computed in memory from a fresh 1-year yfinance pull using the same formulas as the agents; verified against the database values
- Runs automatically each US trading day via GitHub Actions; missed or failed days are left as gaps, never backfilled
- Logs signals, not trades

## Known limitations
- 5-year results (Sept 2021 to Sept 2026) could not distinguish any strategy from buy-and-hold (all 12 comparisons inconclusive)
- Lower volatility and shallower drawdowns for both strategies are partly mechanical (time spent in cash), not proof of skill
## 2026-10-14: Forward log incident (10-13 rows)
- The bot's run for signal date 2026-10-13 (logged 2026-10-14T00:56 UTC) wrote 12 rows with blank confidence and close. Cause (hypothesis, not verified): Yahoo returned a NaN close for the latest bar, NaN comparisons evaluated False, and the script logged fake HOLD/SELL signals.
- Fix 1: log_signals.py now raises if close, MAs or RSI are NaN in the last 2 bars (commit 0ccea04).
- Fix 2: the 12 bad rows were deleted and recomputed at 2026-10-14T10:53 UTC, before the 10-13 signals could be traded (execution is the 10-14 close). Values checked for consistency with 10-12.
- Known weakness: the script logs only the latest bar, so a missed run is a permanent gap. Possible catch-up mode later.

## 2026-10-22: Forward log outage and late-row rule
- From 2026-10-14 to 2026-10-21 the daily workflow failed (red X), because Yahoo returned a latest bar with NaN OHLC (volume present) for all 6 tickers, which the NaN guard correctly refused. Cause on Yahoo's side is unverified. I did not check the Actions tab for 8 days: monitoring failure.
- Signal dates 2026-10-14 to 2026-10-19 were never logged live. 
- Fix: log_signals.py skips trailing NaN bars (printing each one), uses the latest complete bar, and raises if that bar is more than 5 days old.
- Rule: a row counts as LIVE only if logged_at_utc is before the close of the next trading day (execution time). Later rows are LATE/backfill and are excluded from forward-test results. The 2026-10-20 rows are late (logged 2026-10-22).

## 2026-10-22: Correction and recovery
- Missing signal dates (never logged): 2026-10-14, 10-15, 10-16, 10-19, 10-20 (60 rows). Only backfill is possible; backfill rows never count toward live results.
- Workflow failure found in a manual run: Commit step rejected with "fetch first" (remote moved during the run). Fix: git pull --rebase origin main before git push (commit b95c7b4). Cause of runs #5-#10 failing still unverified.
- Manual run #11 (2026-10-22 11:25 UTC) logged 12 rows for signal date 2026-10-21. LIVE (logged before the 20:00 UTC execution close). Yahoo's 10-21 bar was NaN at 11:20 UTC on my Mac and filled by 11:25 UTC on the runner (cause unknown).

## 2026-10-22: Backtest data freeze
- Backtest data: Postgres prices table, 6 tickers x 2514 rows each, 2016-10-10 to 2026-10-09. Checked for duplicates and NaN: none (all columns NOT NULL, rows = distinct dates per ticker).
- The dataset stays frozen at 2026-10-09 for all Week 5 results. No reload until Week 5 is written up, because Yahoo's newest bars have been unreliable.
- Known weakness: no unique constraint on (ticker, date). To add later.
