import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "."))

import plotly.graph_objects as go
from db import SessionLocal
from models.price import Price
from agents.momentum_agent import get_momentum_signals
from agents.mean_reversion_agent import get_mean_reversion_signals

TICKER = "AAPL"

def get_price_series(ticker, session):
    rows = (
        session.query(Price)
        .filter(Price.ticker == ticker)
        .order_by(Price.date)
        .all()
    )
    dates = [r.date for r in rows]
    closes = [r.close for r in rows]
    return dates, closes

def main():
    session = SessionLocal()

    dates, closes = get_price_series(TICKER, session)
    momentum = get_momentum_signals(TICKER, session)
    mean_rev = get_mean_reversion_signals(TICKER, session)

    fig = go.Figure()

    # Base price line
    fig.add_trace(go.Scatter(
        x=dates, y=closes,
        mode="lines", name="AAPL Close Price",
        line=dict(color="lightgray", width=1)
    ))

    # Momentum BUY/SELL markers
    mom_buy = momentum[momentum["signal"] == "BUY"]
    mom_sell = momentum[momentum["signal"] == "SELL"]

    fig.add_trace(go.Scatter(
        x=mom_buy["date"], y=mom_buy["ma_short"],
        mode="markers", name="Momentum BUY",
        marker=dict(color="green", size=10, symbol="triangle-up")
    ))
    fig.add_trace(go.Scatter(
        x=mom_sell["date"], y=mom_sell["ma_short"],
        mode="markers", name="Momentum SELL",
        marker=dict(color="red", size=10, symbol="triangle-down")
    ))

    # Mean-Reversion BUY/SELL markers
    # We need price at each signal date to plot them meaningfully on the price line
    price_lookup = dict(zip(dates, closes))
    mr_buy = mean_rev[mean_rev["signal"] == "BUY"]
    mr_sell = mean_rev[mean_rev["signal"] == "SELL"]

    fig.add_trace(go.Scatter(
        x=mr_buy["date"], y=[price_lookup.get(d) for d in mr_buy["date"]],
        mode="markers", name="Mean-Reversion BUY",
        marker=dict(color="blue", size=6, symbol="circle")
    ))
    fig.add_trace(go.Scatter(
        x=mr_sell["date"], y=[price_lookup.get(d) for d in mr_sell["date"]],
        mode="markers", name="Mean-Reversion SELL",
        marker=dict(color="orange", size=6, symbol="circle")
    ))

    fig.update_layout(
        title=f"{TICKER} — Momentum vs Mean-Reversion Signals",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        template="plotly_dark"
    )

    fig.write_html("signal_chart.html")
    print("Chart saved to signal_chart.html — open it in your browser.")

    session.close()

if __name__ == "__main__":
    main()
