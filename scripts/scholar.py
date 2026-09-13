import json
import os
import re
import urllib.request
from datetime import datetime, timezone

USER = "R87Z5zAAAAAJ"
URL = f"https://scholar.google.com/citations?user={USER}&hl=en"


def fetch():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    try:
        return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
    except Exception as exc:
        print(f"Scholar fetch failed; using previous values: {exc}")
        return ""


def grab(html, pattern):
    match = re.search(pattern, html)
    return int(match.group(1)) if match else None


def parse_metrics(html):
    h_index = grab(html, r"h-index</a></td>\s*<td[^>]*>(\d+)")
    i10 = grab(html, r"i10-index</a></td>\s*<td[^>]*>(\d+)")

    if h_index is None:
        h_index = grab(html, r'h-index</td>\s*<td class="gsc_rsb_std">(\d+)')
    if i10 is None:
        i10 = grab(html, r'i10-index</td>\s*<td class="gsc_rsb_std">(\d+)')

    return {
        "citations": grab(html, r'content="[^"]*Cited by\s+(\d+)'),
        "h_index": h_index,
        "i10": i10,
    }


def previous_value(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            return int(json.load(f).get("message"))
    except (OSError, TypeError, ValueError):
        return None


def write_payload(path, label, value, color):
    payload = {"schemaVersion": 1, "label": label, "message": str(value), "color": color}
    with open(path, "w") as f:
        json.dump(payload, f)


def update(output_dir="."):
    html = fetch()
    metrics = parse_metrics(html)
    data = {
        "gs_data_citations.json": ("citations", "Citations", "blue"),
        "gs_data_h_index.json": ("h_index", "h-index", "blueviolet"),
        "gs_data_i10_index.json": ("i10", "i10-index", "ff69b4"),
    }

    values = {}
    used_fallback = []
    for filename, (key, label, color) in data.items():
        value = metrics[key]
        if value is None:
            path = os.path.join(output_dir, filename)
            previous = previous_value(path)
            value = previous if previous is not None else 0
            used_fallback.append(key)
        values[key] = value
        write_payload(os.path.join(output_dir, filename), label, value, color)

    last_updated = datetime.now(timezone.utc).date().isoformat()
    write_payload(
        os.path.join(output_dir, "gs_data_last_updated.json"),
        "Last updated",
        last_updated,
        "8c1eff",
    )

    result = dict(values)
    result["last_updated"] = last_updated
    result["used_fallback"] = used_fallback
    return result


if __name__ == "__main__":
    print(update())
