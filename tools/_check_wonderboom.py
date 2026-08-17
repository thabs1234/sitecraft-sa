import csv, re
for r in csv.DictReader(open("outreach/outreach-tracker.csv", encoding="utf-8")):
    if "wonderboom" in r["sample_url"]:
        print("TRACKER:", r["area"], "|", r["name"], "|", r["sample_url"])
t = open("samples/durban/intercare-medical-centre-wonderboom.html", encoding="utf-8").read()
m = re.search(r"query=([0-9.,\-]+)", t)
print("MAPS coords:", m.group(1) if m else "none")
lab = re.search(r"Intercare Medical Centre &middot; ([A-Za-z ]*)<", t)
print("SAMPLE label:", lab.group(1) if lab else "none")
