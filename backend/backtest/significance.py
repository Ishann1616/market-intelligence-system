import numpy as np
import pandas as pd

TRADING_DAYS = 252

def sharpe(returns: np.ndarray) -> float:
    std = returns.std(ddof=1)
    if std == 0:
        return 0.0
    return returns.mean() / std * np.sqrt(TRADING_DAYS)

def daily_returns(values: pd.Series) -> np.ndarray:
    return values.reset_index(drop=True).pct_change().dropna().to_numpy()

def block_resample_indices(n: int, block_size: int, rng) -> np.ndarray:
    n_blocks = int(np.ceil(n / block_size))
    starts = rng.integers(0, n - block_size + 1, size=n_blocks)
    idx = np.concatenate([np.arange(s, s + block_size) for s in starts])
    return idx[:n]

def bootstrap_sharpe(strategy_values, benchmark_values, n_iter=5000, block_size=10, seed=42):
    s = daily_returns(strategy_values)
    b = daily_returns(benchmark_values)
    assert len(s) == len(b), "curves must cover the same days"
    n = len(s)
    rng = np.random.default_rng(seed)

    s_boot = np.empty(n_iter)
    diff_boot = np.empty(n_iter)

    for i in range(n_iter):
        idx = block_resample_indices(n, block_size, rng)  # same days for both = paired
        s_sharpe = sharpe(s[idx])
        b_sharpe = sharpe(b[idx])
        s_boot[i] = s_sharpe
        diff_boot[i] = s_sharpe - b_sharpe

    observed_diff = sharpe(s) - sharpe(b)

    return {
        "sharpe": float(round(sharpe(s), 3)),
        "sharpe_ci": (float(round(np.percentile(s_boot, 2.5), 2)),
                      float(round(np.percentile(s_boot, 97.5), 2))),
        "diff_vs_bh": float(round(observed_diff, 3)),
        "diff_ci": (float(round(np.percentile(diff_boot, 2.5), 2)),
                    float(round(np.percentile(diff_boot, 97.5), 2))),
    }