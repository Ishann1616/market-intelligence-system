import os
import re
import csv
import collections
import urllib.request

URL = "https://huggingface.co/datasets/Zihan1004/FNSPID/resolve/main/Stock_news/nasdaq_exteral_data.csv"
OUT_DIR = os.path.expanduser("~/fnspid_extract")
os.makedirs(OUT_DIR, exist_ok=True)
MARGIN = 400_000
RANGES = {
    "AAPL": (84_228_149, 147_467_407),
    "KO":   (9_803_993_041, 9_860_962_890),
    "MSFT": (10_481_089_233, 10_544_328_491),
    "NVDA": (11_307_697_204, 11_372_163_085),
    "TSLA": (15_031_453_673, 15_089_377_563),
}
ROW = re.compile(
    r'^[\d.]*,(\d{4}-\d{2}-\d{2}) ([\d:]{8}) UTC,("(?:[^"]|"")*"|[^,\n]*),([A-Z][A-Z.\-]*),http',
    re.M)

def fetch(lo, hi):
    parts, step = [], 16_000_000
    for s in range(lo, hi, step):
        e = min(s + step - 1, hi)
        req = urllib.request.Request(URL, headers={"Range": f"bytes={s}-{e}"})
        parts.append(urllib.request.urlopen(req).read())
    return b"".join(parts).decode("utf-8", "replace")

for tk, (a, b) in RANGES.items():
    text = fetch(max(0, a - MARGIN), b + MARGIN)
    rows = []
    for m in ROW.finditer(text):
        if m.group(4) == tk:
            title = m.group(3).strip('"').replace('""', '"')
            rows.append((m.group(1), m.group(2), title, tk))
    path = os.path.join(OUT_DIR, f"{tk}_news.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "time", "title", "ticker"])
        w.writerows(rows)

    dates = sorted(r[0] for r in rows)
    real_time = sum(1 for r in rows if r[1] != "00:00:00")
    by_year = collections.Counter(d[:4] for d in dates)
    top = collections.Counter(r[2] for r in rows).most_common(3)
    print(f"\n=== {tk}: {len(rows)} rows, {dates[0] if dates else '-'} to {dates[-1] if dates else '-'}")
    print("  with real time of day: %.1f%%" % (100 * real_time / max(1, len(rows))))
    print("  per year:", dict(sorted(by_year.items())))
    print("  most repeated titles:", [(t[:60], n) for t, n in top])
