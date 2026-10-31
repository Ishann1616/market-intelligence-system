import pandas as pd

from agents.momentum_agent import get_momentum_signals
from agents.mean_reversion_agent import get_mean_reversion_signals
from backtest.engine_v2 import signals_to_exposure

def get_agent_states(ticker, session, prices):
    mom = get_momentum_signals(ticker, session)
    mr = get_mean_reversion_signals(ticker, session)

    common_start = max(mom["date"].min(), mr["date"].min())
    mom = signals_to_exposure(mom[mom["date"] >= common_start]).rename(columns={"exposure": "mom"})
    mr = signals_to_exposure(mr[mr["date"] >= common_start]).rename(columns={"exposure": "mr"})

    states = mom.merge(mr, on="date", how="inner")
    return states.merge(prices[["date", "close"]], on="date", how="inner")