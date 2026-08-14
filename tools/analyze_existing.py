import csv, json, re, os

def norm(p):
    if not p: return None
    x = re.sub(r'[^\d]', '', p)
    if x.startswith('27') and len(x) >= 11: return '+' + x
    if x.startswith('0') and len(x) == 10: return '+27' + x[1:]
    if len(x) == 9: return '+27' + x
    return None

# township leads with real phones
tp = os.path.join("outreach", "township_leads_2026.csv")
with open(tp, encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
phones = sum(1 for r in rows if r.get("phone") and r.get("send_status") != "no_phone")
print("township_leads total rows:", len(rows), "| with phone & sendable:", phones)

# wa_prospects with clean phones
d = json.load(open("/c/Users/Thabang/sitecraft/wa_prospects.json", encoding="utf-8"))
clean = [p for p in d if norm(p.get("phone")) and '*' not in (p.get('phone') or '')]
print("wa_prospects total:", len(d), "| with clean phone:", len(clean))
for p in clean[:8]:
    print("   ", p['city'], "|", p['name'], "|", p['type'], "|", norm(p['phone']))
