# Week 5: Does an adaptive manager beat a fixed 50/50 split?

## Question
I have two simple trading agents. Momentum is "in the stock" when the short moving average is above the long one. Mean-reversion is "in the stock" after the RSI says oversold, and "in cash" after it says overbought.

The question: if a manager gives more money to whichever agent did better over the last 30 days, does it beat just splitting money 50/50 between them?

I wrote the design down in `docs/assumptions_log.md` and committed it BEFORE writing any manager code. That means I could not tune things after seeing results. Fixed in advance: lookback 30 days, trust weights = recent returns floored at 0 and normalized, costs 0.1% of the amount traded, and success = average Sharpe across 6 stocks, tested against buy-and-hold and against static 50/50.

## Method
Data: 6 US stocks (AAPL, TSLA, JPM, KO, NVDA, MSFT), 2465 trading days each (2016-12-19 to 2026-10-09). The database was frozen at 2026-10-09 so results can be reproduced.

Each piece of code exists for one reason:

- **`signals_to_exposure`** (engine_v2.py): the agents say BUY, SELL or HOLD. The engine needs a number: how much of the money is in the stock. This turns BUY into 1, SELL into 0, and HOLD keeps yesterday's value.
- **`run_backtest_v2`** (engine_v2.py): the old engine could only be all-in or all-out. The manager says things like "80% in the stock", so I needed an engine that accepts any number from 0 to 1. It trades at the next day's close (to avoid using future information) and pays 0.1% on the amount traded.
- **`get_agent_states`** (agent_states.py): the manager must compare the two agents on the same days. This lines both agents up from a common start date and joins them with the stock price.
- **`trailing_returns`** (manager.py): measures how much each agent earned over the last 30 days. It uses the agent's state from two days earlier, because that is the state that actually earned today's return. Using yesterday's state would leak future information.
- **`manager_exposure`** (manager.py): turns those trailing returns into trust weights (e.g. 0.8 and 0.2) and blends the agents' in/out states into one exposure number.
- **`static_exposure`** (manager.py): the fair opponent. It always gives each agent weight 0.5, ignoring performance. If the manager cannot beat this, the "adaptive" part adds nothing.
- **`bootstrap_sharpe`** (significance.py): one Sharpe number can be luck. This reshuffles blocks of 10 days 5,000 times and asks whether the difference between two strategies is bigger than noise.

How I checked it (every bug I found earlier was caught by checking, not trusting):
- Engine v2 gave identical results to the old engine on random data and on real AAPL momentum signals (+367.51%).
- A 50% position and a move from 0.8 to 0.3 exposure were calculated by hand first. The engine matched to the cent.
- The manager was checked on a 6-day fake stock with answers worked out on paper.
- AAPL, momentum, mean-reversion and buy-and-hold numbers all matched my earlier results.

## Result
Average Sharpe over 6 stocks (higher is better):

| Strategy | Average Sharpe |
|---|---|
| Buy & Hold | 0.909 |
| Static 50/50 | 0.744 |
| Manager (lookback 30) | 0.685 |
| Momentum | 0.625 |
| Mean-Reversion | 0.552 |

- Manager vs Static 50/50: worse on average (-0.059). Better on only 1 of 6 stocks (TSLA). No stock showed a significant difference.
- Manager vs Buy & Hold: worse on all 6 stocks. Significantly worse on MSFT only; the other five are inconclusive.
- The pre-registered success criterion was NOT met.

## Findings
1. The adaptive manager did not beat a fixed split.
2. Static 50/50 beat both agents on their own (0.744 vs 0.625 and 0.552). The agents disagree on about 70-80% of days and are negatively correlated (about -0.5), so blending them smooths the ride even though neither is good alone.
3. The manager trades far more than 50/50 (hundreds of trades vs about 100 per stock). Each change costs 0.1%, so cost may explain part of the gap. This is a guess. I have not measured it.

## Limits
- The 6 stocks are hand-picked mega-cap winners (NVDA ~92x, TSLA ~28x over 10 years), which makes buy-and-hold very hard to beat.
- The stocks move together, so they are not 6 independent tests.
- The bootstrap tests each stock separately. My pre-registered metric was the average across stocks, which I report as a plain number without a formal test.
- Only 10 years of data, with one lookback pre-registered.

## What I did not do
- I did not change any setting after seeing results.
- I also ran lookbacks 20, 45 and 60 (average Sharpe 0.759, 0.679, 0.647). These are shown for information only. Lookback 20 looks slightly better than 30 but I chose 30 beforehand, and the gap is inside the noise. Any follow-up on shorter windows is exploratory.
- I did not bootstrap static 50/50 against buy-and-hold. It was not pre-registered, so any such test would be exploratory.
