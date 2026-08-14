#!/usr/bin/env python3
"""SiteCraft SA daily build (cron, Day 4+).
For each fresh Overpass prospect (no-site + phone):
  1. generates a real, self-contained mobile-first sample site -> samples/today/<slug>.html
  2. writes a personalized WhatsApp MSG1 (proven hook) + wa.me link
  3. appends a row to outreach-tracker.csv (status=queued)
Stdlib only. Phone numbers are real on disk (display layer masks them).
"""
import json, re, os, csv, urllib.parse, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SAMPLES_DIR = os.path.join(ROOT, "samples", "today")
os.makedirs(SAMPLES_DIR, exist_ok=True)
BASE = "https://thabs1234.github.io/sitecraft-sa/samples/today"
TRACKER = os.path.join(ROOT, "outreach", "outreach-tracker.csv")
DATE = datetime.date.today().isoformat()

SERVICES = {
    "supermarket": ["Groceries & fresh produce", "Specials & weekly deals", "Loyalty specials", "Delivery options"],
    "convenience": ["Everyday essentials", "Snacks & drinks", "Airtime & electricity", "Open early till late"],
    "clinic": ["Consultations", "Chronic medication", "Minor procedures", "Health screenings"],
    "hospital": ["24/7 emergency", "Inpatient care", "Specialist consults", "Maternity"],
    "pharmacy": ["Prescription fills", "OTC medicine", "Vitamins & supplements", "Health advice"],
    "chemist": ["Prescription fills", "OTC medicine", "Vitamins & supplements", "Health advice"],
    "hairdresser": ["Haircuts & styling", "Relaxers & treatments", "Braids & locs", "Kids cuts"],
    "salon": ["Hair & nails", "Facials", "Makeup", "Wedding packages"],
    "medical": ["Consultations", "Chronic care", "Screenings", "Referrals"],
    "primary": ["Quality education", "Aftercare", "Extracurriculars", "Enrolment info"],
    "default": ["Our services", "Walk-ins welcome", "Quality you can trust", "Ask us anything"],
}

def slug(name):
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s or "business"

def clean_phone(phone):
    d = re.sub(r"\D", "", phone)
    if len(d) >= 11:
        return "+" + d[:11]
    if len(d) == 9:
        return "+27" + d
    return None

def wa_digits(phone):
    return re.sub(r"\D", "", phone)[:11]

def pick_services(typ):
    t = typ.lower()
    for k, v in SERVICES.items():
        if k in t:
            return v
    return SERVICES["default"]

TPL = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{name} — {type} | SiteCraft SA sample</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0;font-family:Segoe UI,Roboto,Helvetica,Arial,sans-serif}}
.banner{{background:#0a7d3e;color:#fff;font-size:13px;text-align:center;padding:7px 10px}}
.banner a{{color:#fff;text-decoration:underline}}
.hero{{background:linear-gradient(135deg,#0a7d3e,#13a04f);color:#fff;padding:38px 18px;text-align:center}}
.hero h1{{font-size:27px;margin-bottom:6px}}
.hero p{{opacity:.92;font-size:15px}}
.card{{background:#fff;border-radius:14px;padding:18px;margin:-22px 14px 0;box-shadow:0 6px 20px rgba(0,0,0,.12)}}
h2{{font-size:18px;color:#0a7d3e;margin:18px 14px 8px}}
ul{{list-style:none;margin:0 14px}}
li{{background:#f3f8f4;border-radius:10px;padding:11px 14px;margin-bottom:8px;font-size:15px}}
.contact a{{display:block;text-decoration:none;color:#fff;background:#25D366;border-radius:12px;
  padding:15px;text-align:center;font-weight:700;font-size:16px;margin:14px}}
.contact a.call{{background:#0a7d3e}}
.map a{{display:block;text-align:center;color:#0a7d3e;font-weight:600;padding:10px;text-decoration:none}}
.meta{{color:#555;font-size:14px;margin:6px 14px}}
.foot{{text-align:center;color:#888;font-size:12px;padding:18px}}
</style></head><body>
<div class="banner">FREE sample built by <a href="https://thabs1234.github.io/sitecraft-sa/">SiteCraft SA</a> — no payment needed to claim it.</div>
<div class="hero"><h1>{name}</h1><p>{type} · {area}</p></div>
<div class="card">
  <p style="font-size:15px;color:#333">Welcome to {name}. We serve {area} with quality you can trust.
  This is a free sample site — your real one can be live in 48 hours.</p>
</div>
<h2>What we offer</h2><ul>{services}</ul>
<div class="contact">
  <a class="call" href="tel:{tel}">📞 Call {tel_disp}</a>
  <a href="https://wa.me/{wa}?text=Hi%20{name}%2C%20I%20saw%20my%20sample%20site">💬 WhatsApp us</a>
</div>
<h2>Find us</h2><p class="meta">{addr}</p>
<div class="map"><a href="https://www.google.com/maps/search/?api=1&query={lat},{lon}">📍 Get directions</a></div>
<div class="foot">Sample by SiteCraft SA · R1,500 setup + R450/mo · wa.me/27745086001</div>
</body></html>"""

def render(p):
    svc = "".join(f"<li>{s}</li>" for s in pick_services(p["type"]))
    tel = clean_phone(p["phone"]) or ""
    tel_disp = (tel[1:] if tel.startswith("+") else tel)
    wa = wa_digits(p["phone"])
    html = TPL.format(name=p["name"], type=p["type"], area=p["area"], services=svc,
                      tel=tel, tel_disp=tel_disp, wa=wa, addr=p.get("addr") or f"{p['area']}, Gauteng",
                      lat=p.get("lat") or "", lon=p.get("lon") or "")
    s = slug(p["name"])
    path = os.path.join(SAMPLES_DIR, s + ".html")
    # avoid slug collisions
    i = 1
    while os.path.exists(path):
        s = f"{slug(p['name'])}-{p['area'].lower()}-{i}"; path = os.path.join(SAMPLES_DIR, s + ".html"); i += 1
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return s

def main():
    data = json.load(open(os.path.join(HERE, "prospect_today.json"), encoding="utf-8"))
    rows = []
    built = 0
    for p in data:
        phone = clean_phone(p["phone"])
        if not phone:
            continue
        s = render(p)
        url = f"{BASE}/{s}.html"
        wa = wa_digits(p["phone"])
        msg = (f"Hi {p['name']} 👋 I'm Thabang from SiteCraft SA. I noticed you don't have a "
               f"website, so I built you a free sample — no catch, nothing owed: {url}\n"
               f"Most customers in {p['area']} search Google before they call; right now they "
               f"find your competitors, not you. Want me to walk you through it? (2 min)")
        wa_link = f"https://wa.me/{wa}?text={urllib.parse.quote(msg)}"
        rows.append({
            "date": DATE, "area": p["area"], "name": p["name"], "type": p["type"],
            "phone": phone, "sample_url": url, "message": msg, "wa_link": wa_link,
            "send_status": "queued", "source": "overpass",
        })
        built += 1
    # write tracker (append if exists, else new with header)
    cols = ["date", "area", "name", "type", "phone", "sample_url", "message", "wa_link", "send_status", "source"]
    write_header = not os.path.exists(TRACKER)
    with open(TRACKER, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        if write_header:
            w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"SAMPLES BUILT: {built}")
    print(f"TRACKER ROWS ADDED: {len(rows)} -> {TRACKER}")
    print(f"First sample: {rows[0]['sample_url'] if rows else 'n/a'}")

if __name__ == "__main__":
    main()
