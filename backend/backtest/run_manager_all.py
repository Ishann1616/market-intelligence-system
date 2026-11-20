import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from db import SessionLocal
from models.price import Price
from backtest.agent_states import get_agent_states
from backtest.engine_v2 import run_backtest_v2
from backtest.manager import manager_exposure, static_exposure
from backtest.metrics import compute_metrics
from backtest.significance import bootstrap_sharpe
from backtest.run_significance import verdict

TICKERS =["AAPL","TSLA", "JPM", "KO", "NVDA", "MSFT"]
LOOKBACK = 30
SENSITIVITY = [20, 45, 60]

def get_price_df(ticker, session):
    rows = session.query(Price).filter(Price.ticker == ticker).order_by(Price.date).all()
    return pd.DataFrame([{"date": r.date, "close": r.close} for r in rows])

def curve(expo_df, p):
    return run_backtest_v2(expo_df,p)["portfolio_value"]

def main():
    session = SessionLocal()
    sharpe_rows, boot_rows, sens_rows =[],[], []

    for t in TICKERS:
        states = get_agent_states(t, session, get_price_df(t, session))
        p = states[["date", "close"]]
        curves = {
            "Manager": curve(manager_exposure(states, LOOKBACK), p),
            "Static 50/50": curve(static_exposure(states), p),
            "Momentum": curve(states[["date"]].assign(exposure=states["mom"]), p),
            "Mean-Reversion": curve(states[["date"]].assign(exposure=states["mr"]), p),
            "Buy & Hold": states["close"] / states["close"].iloc[0] * 10000,
        }
        sharpe_rows.append({"ticker":t, **{k: compute_metrics(v)["sharpe"] for k, v in curves.items()}})

        for bench in ["Buy & Hold", "Static 50/50"]:
            r = bootstrap_sharpe(curves["Manager"], curves[bench])
            boot_rows.append({"ticker": t, "vs":bench, "diff": r["diff_vs_bh"],
                              "diff_95%_CI": r["diff_ci"], "verdict":verdict(r["diff_ci"])})

        sens = {"ticker": t}
        for lb in SENSITIVITY:
                        sens[f"lb{lb}"] = compute_metrics(curve(manager_exposure(states, lb), p))["sharpe"]
        sens_rows.append(sens)

    session.close()

    sh = pd.DataFrame(sharpe_rows)
    print("\n===== SHARPE BY TICKER (lookback 30) =====")
    print(sh.to_string(index=False))
    print("\n===== AVERAGE SHARPE =====")
    print(sh.drop(columns="ticker").mean().round(3).to_string())
    print("\n===== BOOTSTRAP: Manager vs benchmark (diff = Manager - benchmark) =====")
    print(pd.DataFrame(boot_rows).to_string(index=False))
    print("\n===== SENSITIVITY: Manager Sharpe at other lookbacks (not for selection) =====")
    print(pd.DataFrame(sens_rows).to_string(index=False))

if __name__ == "__main__":
    main()