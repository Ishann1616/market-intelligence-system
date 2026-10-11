import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from db import SessionLocal
from backtest.compare_metrics import build_curves, TICKERS
from backtest.significance import bootstrap_sharpe

def verdict(diff_ci):
    low, high = diff_ci
    if low > 0:
        return "BETTER"
    if high < 0:
        return "WORSE"
    return "inconclusive"

def main():
    session = SessionLocal()
    rows = []

    for ticker in TICKERS:
        curves = build_curves(ticker, session)
        for name in ["Momentum", "Mean-Reversion"]:
            res = bootstrap_sharpe(curves[name], curves["Buy & Hold"])
            rows.append({
                "ticker": ticker,
                "strategy": name,
                "sharpe": res["sharpe"],
                "sharpe_95%_CI": res["sharpe_ci"],
                "diff_vs_B&H": res["diff_vs_bh"],
                "diff_95%_CI": res["diff_ci"],
                "verdict": verdict(res["diff_ci"]),
            })

    print("\n\n===== BOOTSTRAP SIGNIFICANCE (vs Buy & Hold) =====")
    print(pd.DataFrame(rows).to_string(index=False))
    session.close()

if __name__ == "__main__":
    main()
    