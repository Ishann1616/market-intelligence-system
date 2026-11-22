import os
import re
import csv
import collections
import urllib.request

URL = "https://huggingface.co/datasets/Zihan1004/FNSPID/resolve/main/Stock_news/All_external.csv"
LIMIT = 340_000_000                      # ticker-tagged part ends before this
MARGIN = 400_000
OUT_DIR = os.path.expanduser("~/fnspid_extract")
os.makedirs(OUT_DIR, exist_ok=True)
ROW = re.compile(
    r'^(\d{4}-\d{2}-\d{2}) ([\d:]{8}) UTC,("(?:[^"]|"")*"|[^,\n]*),([A-Z][A-Z.\-]*),http',
    re.M)
ANALYST = re.compile(r"Maintains|Upgrades|Downgrades|Initiates|Reiterates|Price Target", re.I)

def get(lo, hi):
    req = urllib.request.Request(URL, headers={"Range": f"bytes={lo}-{hi}"})
    return urllib.request.urlopen(req).read().decode("utf-8", "replace")

def ticker_at(offset):
    for extra in range(0, 400_000, 100_000):
        m = ROW.search(get(offset + extra, offset + extra + 120_000))
        if m:
            return m.group(4)
    return None

def boundary(target, strict):
    lo, hi = 0, LIMIT
    while hi - lo > 100_000:
        mid = (lo + hi) // 2
        t = ticker_at(mid)
        if t is None:
            hi = mid
            continue
        if (t > target) if strict else (t >= target):
            hi = mid
        else:
            lo = mid
    return lo

for tk in ["AAPL", "JPM", "KO", "MSFT", "NVDA", "TSLA"]:
    a, b = boundary(tk, False), boundary(tk, True)
    text = ""
    for s in range(max(0, a - MARGIN), b + MARGIN, 16_000_000):
        text += get(s, min(s + 16_000_000 - 1, b + MARGIN))
    rows = []
    for m in ROW.finditer(text):
        if m.group(4) == tk:
            rows.append((m.group(1), m.group(2), m.group(3).strip('"').replace('""', '"'), tk))
    with open(os.path.join(OUT_DIR, f"ALLEXT_{tk}.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "time", "title", "ticker"])
        w.writerows(rows)

    print(f"\n=== {tk}: block ~{(b - a) / 1e6:.2f} MB, {len(rows)} rows")
    if not rows:
        continue
    dates = sorted(r[0] for r in rows)
    real = sum(1 for r in rows if r[1] != "00:00:00")
    analyst = sum(1 for r in rows if ANALYST.search(r[2]))
    by_year = collections.Counter(d[:4] for d in dates)
    top = collections.Counter(r[2] for r in rows).most_common(2)
    print(f"  range {dates[0]} to {dates[-1]}, distinct days with news: {len(set(dates))}")
    print("  per year:", dict(sorted(by_year.items())))
    print("  real time of day: %.1f%%, analyst-rating style titles: %.1f%%" % (
        100 * real / len(rows), 100 * analyst / len(rows)))
    print("  most repeated:", [(t[:50], n) for t, n in top])
