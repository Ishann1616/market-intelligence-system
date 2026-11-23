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

## 2026-10-22: Engine v2 rebalancing rule (decided before any manager results)
- Trades happen only when the target exposure changes. No rebalancing for price drift between changes. Cost = 0.1% of the amount traded at each change.
- Target exposure decided with data through day t is applied at the close of day t+1 (same 1-day shift as engine v1). Day 0 target is 0.

## 2026-10-22: Engine v2 rebalancing rule (decided before any manager results)
- Trades happen only when the target exposure changes. No rebalancing for price drift between changes. Cost = 0.1% of the amount traded at each change.
- Target exposure decided with data through day t is applied at the close of day t+1 (same 1-day shift as engine v1). Day 0 target is 0.

## 2026-10-31: Manager trailing-return definition (before any manager results)
- Agent daily return on day k = agent state decided at day k-2 x stock return on day k (matches the engine's 1-day execution shift; uses no future data).
- Trailing return at day t = compounded agent daily returns over days t-29..t (lookback 30). Weights = trailing returns floored at 0, normalized; 50/50 if both are 0 or if the window is not yet full (warmup detail, added here).
- Data frozen at 2026-10-09 (Postgres).

## 2026-11-20: Week 5 result (pre-registered design, lookback 30, data frozen at 2026-10-09)
- Average Sharpe over 6 tickers: Manager 0.685, Static 50/50 0.744, Momentum 0.625, Mean-Reversion 0.552, Buy & Hold 0.909.
- Manager vs Static 50/50: worse on average (-0.059), better on 1 of 6 tickers (TSLA), no significant differences. Manager vs Buy & Hold: worse on 6 of 6, significant on MSFT only. Pre-registered success criterion NOT met.
- Sensitivity (shown, not selected): average Sharpe 0.759 / 0.685 / 0.679 / 0.647 at lookback 20 / 30 / 45 / 60. Primary setting stays 30. Any follow-up on shorter lookbacks is exploratory.
- Raw output: results_week5.txt.

## 2026-11-22: Week 6 data check, historical sentiment backtest NOT feasible
- Checked FNSPID news files on Hugging Face (nasdaq_exteral_data.csv, 23.2 GB; All_external.csv, 5.73 GB). Only the first ~75% / ~6% of them are ticker-tagged stock news; the rest is unrelated news.
- Nasdaq file: AAPL, MSFT, TSLA, NVDA only from 2021-2022 to 2023-12-16 (about 8,700 rows each); KO from 2009; JPM absent. Benzinga file: patchy (AAPL 441 rows, MSFT none found, JPM 10 rows, TSLA from 2019, NVDA and KO longer).
- Timestamps are date-only in 97-99% of rows. No window covers all 6 tickers; best common window is about 2022-06 to 2023-12 for 5 tickers (about 320 usable days), which has too little power for a meaningful test.
- Decision: no historical sentiment backtest. Sentiment is collected forward only, with fetch time stored per headline. Any later result is exploratory.
- Raw data stays outside the repo (third-party licences); only the probe scripts are committed (backend/data/news_probe/).

## 2026-11-23: Week 7 API, live/late labelling in /signals/latest
- A signal row is LIVE if logged_at_utc is before the close of the next trading day, otherwise LATE. Late rows are excluded from forward-test results.
- Next trading day = next weekday not in a hardcoded holiday list (2026-11-26, 2026-12-25). The list must be extended by hand for later dates.
- Execution close is 20:00 UTC before 2026-11-02 and 21:00 UTC from 2026-11-02 (US clock change).
- Known approximation: the early close on the day after Thanksgiving is ignored. A row logged near that cutoff could be mislabelled by up to 3 hours.
- Result as of 2026-11-23: 276 rows, 23 signal dates, 216 live and 60 late. The late dates are 10-22, 10-23, 10-26, 11-03 and 11-04.
- Hand-check: AAPL momentum rows for the 5 late dates were each logged 4 to 5 hours after the cutoff, and the 11-02 row was logged about 17.5 hours before it. All 6 matched their labels. Only one ticker and one agent were checked per date.
