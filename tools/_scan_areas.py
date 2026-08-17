import csv, re
DURBAN_OK = {"berea", "morningside", "glenwood", "umbilo", "durban north", "westville",
             "pinetown", "kloof", "chatsworth", "umhlanga", "durban", "queensburgh",
             "amanzimtoti", "pende", "yellowwood park", "athlone", "glenhills"}
bad = []
for r in csv.DictReader(open("outreach/outreach-tracker.csv", encoding="utf-8")):
    if r["date"] == "2026-08-16":
        if r["area"].strip().lower() not in DURBAN_OK:
            bad.append((r["area"], r["name"], r["sample_url"]))
print("anomalous areas today:", bad)
