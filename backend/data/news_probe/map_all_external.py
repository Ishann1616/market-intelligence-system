import re
import urllib.request

URL = "https://huggingface.co/datasets/Zihan1004/FNSPID/resolve/main/Stock_news/All_external.csv"
STEP = 10_000_000
LIMIT = 700_000_000
ROW = re.compile(
    r'^(\d{4}-\d{2}-\d{2}) [\d:]{8} UTC,(?:"(?:[^"]|"")*"|[^,\n]*),([A-Z][A-Z.\-]*),http',
    re.M)

prev = ""
for off in range(0, LIMIT, STEP):
    req = urllib.request.Request(URL, headers={"Range": f"bytes={off}-{off + 120_000}"})
    text = urllib.request.urlopen(req).read().decode("utf-8", "replace")
    m = ROW.search(text)
    tk, dt = (m.group(2), m.group(1)) if m else ("NONE", "")
    flag = ""
    if prev and tk != "NONE" and tk < prev:
        flag = "  <-- order break"
    print(f"{off / 1e6:6.0f} MB  {tk:8s} {dt}{flag}")
    if tk != "NONE":
        prev = tk
