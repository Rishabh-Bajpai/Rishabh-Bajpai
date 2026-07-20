import json
import os
import subprocess


def totals(account, kind):
    # kind: "users" or "orgs"
    out = subprocess.run(
        ["gh", "api", f"{kind}/{account}/repos?per_page=100", "--jq", "."],
        capture_output=True,
        text=True,
    )
    try:
        repos = json.loads(out.stdout)
    except Exception:
        return 0, 0
    repos = [r for r in repos if not r.get("fork")]
    stars = sum(r.get("stargazers_count", 0) for r in repos)
    forks = sum(r.get("forks_count", 0) for r in repos)
    return stars, forks


ps, pf = totals("Rishabh-Bajpai", "users")
ss, sf = totals("samosa-ai-com", "orgs")
stars = ps + ss
forks = pf + sf

data = {
    "total_stars.json": ("Total Stars", stars, "8c1eff"),
    "total_forks.json": ("Total Forks", forks, "0e7490"),
}

for filename, (label, value, color) in data.items():
    # keep previous value if live fetch returned 0 (likely rate-limited / blocked)
    if value == 0 and os.path.exists(filename):
        try:
            value = int(json.load(open(filename)).get("message", value))
        except Exception:
            pass
    payload = {"schemaVersion": 1, "label": label, "message": str(value), "color": color}
    with open(filename, "w") as f:
        json.dump(payload, f)

print({"personal": (ps, pf), "samosa": (ss, sf), "total": (stars, forks)})
