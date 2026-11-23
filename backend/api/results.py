import re
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter()

RESULTS_PATH = Path(__file__).resolve().parents[2] / "results_week5.txt"
STRATEGIES = ["Manager", "Static 50/50", "Momentum", "Mean-Reversion", "Buy & Hold"]

BOOT_RE = re.compile(
    r"^\s*(\w+)\s+(Buy & Hold|Static 50/50)\s+(-?\d+\.\d+)\s+"
    r"\((-?[\d.]+),\s*(-?[\d.]+)\)\s+(\w+)\s*$"
)


def split_sections(text):
    # Header lines start with "=====". Everything under a header belongs to it.
    sections, key = {}, None
    for line in text.splitlines():
        if line.startswith("====="):
            key = line.strip("= ").strip()
            sections[key] = []
        elif key is not None:
            sections[key].append(line)
    return sections


def find(sections, prefix):
    for k, lines in sections.items():
        if k.startswith(prefix):
            return lines
    raise HTTPException(status_code=500, detail=f"section not found: {prefix}")


def parse_results():
    if not RESULTS_PATH.exists():
        raise HTTPException(status_code=503, detail="results file not found")
    sections = split_sections(RESULTS_PATH.read_text())

    sharpe = []
    for line in find(sections, "SHARPE BY TICKER")[1:]:  # [1:] skips column header
        parts = line.split()
        if len(parts) == 6:
            sharpe.append(
                {"ticker": parts[0], **dict(zip(STRATEGIES, map(float, parts[1:])))}
            )

    average = {}
    for line in find(sections, "AVERAGE SHARPE"):
        if line.strip():
            name, value = line.rsplit(None, 1)
            average[name.strip()] = float(value)

    bootstrap = []
    for line in find(sections, "BOOTSTRAP"):
        m = BOOT_RE.match(line)
        if m:
            bootstrap.append(
                {
                    "ticker": m.group(1),
                    "vs": m.group(2),
                    "diff": float(m.group(3)),
                    "ci_low": float(m.group(4)),
                    "ci_high": float(m.group(5)),
                    "verdict": m.group(6),
                }
            )

    sensitivity = []
    for line in find(sections, "SENSITIVITY")[1:]:
        parts = line.split()
        if len(parts) == 4:
            sensitivity.append(
                {
                    "ticker": parts[0],
                    "lb20": float(parts[1]),
                    "lb45": float(parts[2]),
                    "lb60": float(parts[3]),
                }
            )

    return sharpe, average, bootstrap, sensitivity


@router.get("/results/summary")
def results_summary():
    sharpe, average, bootstrap, sensitivity = parse_results()

    if (len(sharpe), len(average), len(bootstrap), len(sensitivity)) != (6, 5, 12, 6):
        raise HTTPException(
            status_code=500,
            detail=(
                "parse mismatch: "
                f"{len(sharpe)} sharpe, {len(average)} average, "
                f"{len(bootstrap)} bootstrap, {len(sensitivity)} sensitivity rows"
            ),
        )

    counts = {}
    for bench in ["Buy & Hold", "Static 50/50"]:
        rows = [b for b in bootstrap if b["vs"] == bench]
        counts[bench] = {
            "manager_worse": sum(b["diff"] < 0 for b in rows),
            "manager_better": sum(b["diff"] > 0 for b in rows),
            "significant": sum(b["verdict"] != "inconclusive" for b in rows),
        }

    return {
        "lookback": 30,
        "success_criterion_met": False,
        "sharpe_by_ticker": sharpe,
        "average_sharpe": average,
        "bootstrap_manager_vs": bootstrap,
        "bootstrap_counts": counts,
        "sensitivity_not_for_selection": sensitivity,
    }