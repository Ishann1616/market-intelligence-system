import numpy as np
import pandas as pd

from backtest.manager import manager_exposure


def test_manager_by_hand():
    states = pd.DataFrame({
        "date": pd.bdate_range("2024-01-01", periods=6).date,
        "close": [100.0, 110.0, 99.0, 108.9, 108.9, 119.79],
        "mom": [1.0] * 6,
        "mr": [0.0, 0.0, 1.0, 1.0, 0.0, 0.0],
    })
    out = manager_exposure(states, lookback=3)
    expected = [0.5, 0.5, 1.0, 1.0, 0.5, 0.21 / 0.31]
    assert np.allclose(out["exposure"].values, expected), out["exposure"].tolist()
    print("MANAGER TEST PASSED:", [round(x, 4) for x in out["exposure"]])


if __name__ == "__main__":
    test_manager_by_hand()