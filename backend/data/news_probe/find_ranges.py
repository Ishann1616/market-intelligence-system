import re
import urllib.request

URL = "https://huggingface.co/datasets/Zihan1004/FNSPID/resolve/main/Stock_news/nasdaq_exteral_data.csv"
SIZE = 23_200_000_000                 # approximate, from the 23.2 GB on the page
LIMIT = int(SIZE * 0.77)              # past this the file is not ticker-sorted news
PATTERN = re.compile(
    r'^[\d.]*,(\d{4}-\d{2}-\d{2}) [\d:]{8} UTC,(?:"(?:[^"]|"")*"|[^,\n]*),([A-Z][A-Z.\-]*),http',
    re.M)

def ticker_at(offset):
    for extra in range(0, 600_000, 100_000):      # retry further on if the window has no row start
        start = offset + extra
        req = urllib.request.Request(URL, headers={"Range": f"bytes={start}-{start + 120_000}"})
        text = urllib.request.urlopen(req).read().decode("utf-8", "replace")
        m = PATTERN.search(text)
        if m:
            return m.group(2)
    return None

def boundary(target, strict):
    """Smallest offset whose ticker is >= target (strict=False) or > target (strict=True)."""
    lo, hi = 0, LIMIT
    while hi - lo > 150_000:
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
    a = boundary(tk, strict=False)
    b = boundary(tk, strict=True)
    print(f"{tk:5s} start={a:>14,}  end={b:>14,}  size~{(b - a) / 1e6:8.1f} MB")
