import json
import os
import re
import urllib.request

USER = "R87Z5zAAAAAJ"
URL = f"https://scholar.google.com/citations?user={USER}&hl=en"


def fetch():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    try:
        return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
    except Exception:
        return ""


html = fetch()


def grab(pattern, default=0):
    m = re.search(pattern, html)
    return int(m.group(1)) if m else default


citations = grab(r'content="[^"]*Cited by\s+(\d+)')
h_index = grab(r"h-index</a></td>\s*<td[^>]*>(\d+)")
i10 = grab(r"i10-index</a></td>\s*<td[^>]*>(\d+)")

if h_index == 0:
    m = re.search(r'h-index</td>\s*<td class="gsc_rsb_std">(\d+)', html)
    h_index = int(m.group(1)) if m else 0
if i10 == 0:
    m = re.search(r'i10-index</td>\s*<td class="gsc_rsb_std">(\d+)', html)
    i10 = int(m.group(1)) if m else 0

data = {
    "gs_data_citations.json": ("Citations", citations, "blue"),
    "gs_data_h_index.json": ("h-index", h_index, "blueviolet"),
    "gs_data_i10_index.json": ("i10-index", i10, "ff69b4"),
}

for filename, (label, value, color) in data.items():
    if value == 0 and os.path.exists(filename):
        try:
            prev = json.load(open(filename))
            value = int(prev.get("message", value))
        except Exception:
            pass
    payload = {"schemaVersion": 1, "label": label, "message": str(value), "color": color}
    with open(filename, "w") as f:
        json.dump(payload, f)

print({"citations": citations, "h_index": h_index, "i10": i10})
