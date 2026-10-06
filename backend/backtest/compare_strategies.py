import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import plotly.graph_objects as go
import pandas as pd
from db import SessionLocal
from models.price import Price
from agents.momentum_agent import get_momentum_signals
from agents.mean_reversion_agent import get_mean_reversion_signals
from backtest.engine import run_backtest

TICKER = "AAPL"
STARTING_CAPITAL = 10000

def get_price_df(ticker, session):
    rows = session.query(Price).filter(Price.ticker == ticker).order_by(Price.date).all()
    return pd.DataFrame([{"date": r.date, "close": r.close} for r in rows])

def main():
    session = SessionLocal()

    prices = get_price_df(TICKER, session)
    momentum_signals = get_momentum_signals(TICKER, session)
    mean_rev_signals = get_mean_reversion_signals(TICKER, session)

    momentum_result = run_backtest(momentum_signals, prices, STARTING_CAPITAL)
    mean_rev_result = run_backtest(mean_rev_signals, prices, STARTING_CAPITAL)

    # Buy-and-hold: never sell, value just tracks price directly from day 1
    first_price = prices["close"].iloc[0]
    shares = STARTING_CAPITAL / first_price
    buy_hold_values = prices["close"] * shares

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=prices["date"], y=buy_hold_values,
        mode="lines", name="Buy & Hold",
        line=dict(color="gray", width=2)
    ))
    fig.add_trace(go.Scatter(
        x=momentum_result["date"], y=momentum_result["portfolio_value"],
        mode="lines", name="Momentum",
        line=dict(color="green", width=2)
    ))
    fig.add_trace(go.Scatter(
        x=mean_rev_result["date"], y=mean_rev_result["portfolio_value"],
        mode="lines", name="Mean-Reversion",
        line=dict(color="blue", width=2)
    ))

    fig.update_layout(
        title=f"{TICKER} — Strategy Comparison (Starting Capital: ${STARTING_CAPITAL:,.0f})",
        xaxis_title="Date",
        yaxis_title="Portfolio Value ($)",
        template="plotly_dark"
    )

    fig.write_html("strategy_comparison.html")
    print("Chart saved to strategy_comparison.html — open it in your browser.")

    print(f"\nFinal values:")
    print(f"Buy & Hold:      ${buy_hold_values.iloc[-1]:,.2f}")
    print(f"Momentum:        ${momentum_result['portfolio_value'].iloc[-1]:,.2f}")
    print(f"Mean-Reversion:  ${mean_rev_result['portfolio_value'].iloc[-1]:,.2f}")

    session.close()

if __name__ == "__main__":
    main()
