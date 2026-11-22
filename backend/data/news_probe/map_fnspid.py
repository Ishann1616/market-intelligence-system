import re
import urllib.request

URL = "https://huggingface.co/datasets/Zihan1004/FNSPID/resolve/main/Stock_news/nasdaq_exteral_data.csv"
SIZE = 23_200_000_000   # approximate, from the 23.2 GB on the page
PATTERN = re.compile(
    r'^[\d.]*,(\d{4}-\d{2}-\d{2}) [\d:]{8} UTC,(?:"(?:[^"]|"")*"|[^,\n]*),([A-Z][A-Z.\-]*),http',
    re.M)

def first_ticker(offset):
    req = urllib.request.Request(URL, headers={"Range": f"bytes={offset}-{offset + 120000}"})
    text = urllib.request.urlopen(req).read().decode("utf-8", "replace")
    m = PATTERN.search(text)
    return (m.group(2), m.group(1)) if m else ("NONE", "")

for pct in range(0, 82, 2):
    t, d = first_ticker(int(SIZE * pct / 100))
    print(f"{pct:3d}%  {t:8s} {d}")
