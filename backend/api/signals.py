import csv
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter()

LOG_PATH = Path(__file__).resolve().parents[2] / "logs" / "signal_log.csv"
HOLIDAYS = {date(2026, 11, 26), date(2026, 12, 25)}
DST_END = date(2026, 11, 2)  # first trading day on 21:00 UTC close


def next_trading_day(d):
    d += timedelta(days=1)
    while d.weekday() >= 5 or d in HOLIDAYS:
        d += timedelta(days=1)
    return d


def execution_close_utc(signal_date):
    nxt = next_trading_day(signal_date)
    hour = 21 if nxt >= DST_END else 20
    return datetime.combine(nxt, time(hour, 0), tzinfo=timezone.utc)


def to_float(x):
    return float(x) if x not in ("", None) else None


def read_log():
    if not LOG_PATH.exists():
        raise HTTPException(status_code=503, detail="signal log not found")
    with open(LOG_PATH, newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        sd = date.fromisoformat(r["signal_date"])
        logged = datetime.fromisoformat(r["logged_at_utc"])
        r["status"] = "live" if logged < execution_close_utc(sd) else "late"
        r["confidence"] = to_float(r["confidence"])
        r["close"] = to_float(r["close"])
    return rows


@router.get("/signals/latest")
def signals_latest():
    rows = read_log()
    if not rows:
        raise HTTPException(status_code=404, detail="signal log is empty")
    latest = max(r["signal_date"] for r in rows)
    return {
        "signal_date": latest,
        "rows": [r for r in rows if r["signal_date"] == latest],
        "totals": {
            "rows": len(rows),
            "dates_logged": len({r["signal_date"] for r in rows}),
            "live_rows": sum(r["status"] == "live" for r in rows),
            "late_rows": sum(r["status"] == "late" for r in rows),
        },
    }