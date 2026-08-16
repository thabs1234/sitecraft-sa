import os, csv, re
d = "samples/durban"
bad = 0
for fn in os.listdir(d):
    t = open(os.path.join(d, fn), encoding="utf-8").read()
    if "wa.me/" not in t or "tel:" not in t:
        bad += 1
    if "{name}" in t or "{phone}" in t or "{sample_url}" in t:
        bad += 1
    if "thabs1234.github.io" not in t:
        bad += 1
print("durban sample files:", len(os.listdir(d)), "bad:", bad)

rows = [r for r in csv.DictReader(open("outreach/outreach-tracker.csv", encoding="utf-8"))
        if "durban" in r["sample_url"]]
print("tracker durban rows:", len(rows))
for r in rows[:6]:
    print("  -", r["area"], "|", r["name"], "|", r["type"], "|", r["phone"])

# overall tracker metrics
allrows = list(csv.DictReader(open("outreach/outreach-tracker.csv", encoding="utf-8")))
print("\nTOTAL tracker rows:", len(allrows))
from collections import Counter
print("send_status:", Counter(r["send_status"] for r in allrows))
print("source:", Counter(r["source"] for r in allrows))
print("by date:", Counter(r["date"] for r in allrows))
