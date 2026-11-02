import numpy as np
import pandas as pd

def trailing_returns(states, lookback=30):
    stock_ret = states["close"].pct_change()
    out = {}
    for col in ["mom", "mr"]:
        agent_ret = states[col].shift(2)* stock_ret
        out[col] = (1+agent_ret).rolling(lookback).apply(np.prod, raw=True)-1
    return out

def manager_exposure(states, lookback=30):
    tr = trailing_returns(states, lookback)
    m = tr["mom"].clip(lower=0)
    r = tr["mr"].clip(lower=0)
    total = m + r
    w_mom = (m / total).where(total > 0, 0.5).fillna(0.5)   # 50/50 if both 0 or warmup
    out = states[["date"]].copy()
    out["w_mom"] = w_mom
    out["exposure"] = w_mom * states["mom"] + (1 - w_mom) * states["mr"]
    return out


def static_exposure(states):
    out = states[["date"]].copy()
    out["exposure"] = 0.5 * states["mom"] + 0.5 * states["mr"]
    return out
