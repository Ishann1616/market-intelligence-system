import numpy as np
import pandas as pd 

from backtest.engine import run_backtest
from backtest.engine_v2 import run_backtest_v2, signals_to_exposure

def test_matches_old_engine():
    rng = np.random.default_rng(7)
    n = 500
    dates = pd.bdate_range("2020-01-01", periods=n).date 
    close = 100 * np.cumprod(1 + rng.normal(0.0004, 0.015, n))
    prices = pd.DataFrame({"date": dates, "close": close})
    signals = pd.DataFrame({"date": dates, 
                            "signal": rng.choice(["BUY", "SELL", "HOLD"], n, p= [0.1, 0.1, 0.8])})
    old = run_backtest(signals, prices)
    new = run_backtest_v2(signals_to_exposure(signals), prices)
    assert np.allclose(old["portfolio_value"].values, new["portfolio_value"].values, rtol=1e-9)
    print("TEST 1 PASSED: v2 matches v1. FINAL:",
          round(old["portfolio_value"].iloc[-1], 2), round(new["portfolio_value"].iloc[-1], 2))

def test_partial_position_by_hand():
    prices = pd.DataFrame({"date": pd.bdate_range("2024-01-01", periods=4).date,
                           "close":[100.0 , 100.0, 110.0, 110.0]})
    expo = pd.DataFrame({"date": prices["date"], "exposure": [0.5] * 4})
    out = run_backtest_v2(expo, prices)
    expected = [10000.0, 9995.0, 10494.75, 10494.75]
    assert np.allclose(out["portfolio_value"].values, expected), out["portfolio_value"].tolist()
    print("TEST 2 PASSED: hand-checked partial position")

if __name__ == "__main__":
    test_matches_old_engine()
    test_partial_position_by_hand()