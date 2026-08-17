import urllib.request, csv, time
rows = [r for r in csv.DictReader(open("outreach/outreach-tracker.csv", encoding="utf-8"))
        if r["date"] == "2026-08-16"]
ok = bad = 0
for r in rows:
    u = r["sample_url"]
    try:
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            if resp.status == 200:
                ok += 1
            else:
                bad += 1
                print("NON200", resp.status, r["name"])
    except Exception as e:
        bad += 1
        print("ERR", e, r["name"], u)
print(f"\n2026-08-16 sample URLs -> OK={ok} BAD={bad} (total {len(rows)})")
