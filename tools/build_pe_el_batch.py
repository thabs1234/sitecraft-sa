#!/usr/bin/env python3
"""SiteCraft SA — Gqeberha (Port Elizabeth) + East London batch builder (cron, Day 8+).

Pulls REAL independent businesses that have NO website and a phone from
OpenStreetMap Overpass, builds a real mobile sample site for each, generates a
personalized pitch-gen MSG1 + wa.me click-to-chat link, and appends rows to
outreach-tracker.csv (send_status=queued -> staged for MANUAL send, max 5/day).

Stdlib only. No API key. Honors the ban-safe, free-sample-first design.
Mirrors tools/build_durban_batch.py (proven, Aug 2026).
"""
import urllib.request, urllib.parse, json, time, os, re, csv, html, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_SAMPLES = os.path.join(ROOT, "samples", "pe_el")
CSV_PATH = os.path.join(ROOT, "outreach", "outreach-tracker.csv")
TODAY = datetime.date.today().isoformat()

# Gqeberha (Port Elizabeth) + East London suburbs (independent-business density)
SUBURBS = {
    "Gqeberha-CBD": (-33.9608, 25.6022),
    "Walmer": (-33.9790, 25.5600),
    "Summerstrand": (-33.9850, 25.6500),
    "Newton-Park": (-33.9300, 25.5900),
    "Greenacres": (-33.9450, 25.5700),
    "EastLondon-CBD": (-32.1960, 27.8700),
    "Berea-EL": (-32.2300, 27.9600),
    "Vincent-EL": (-32.2500, 27.9000),
}
CITY = {
    "Gqeberha-CBD": "Gqeberha", "Walmer": "Gqeberha", "Summerstrand": "Gqeberha",
    "Newton-Park": "Gqeberha", "Greenacres": "Gqeberha",
    "EastLondon-CBD": "East London", "Berea-EL": "East London", "Vincent-EL": "East London",
}
RADIUS = 3000

MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
]

SHOPS = ("bakery", "butcher", "clothes", "furniture", "hardware", "florist",
         "jewelry", "optician", "photo", "tailor", "tattoo", "chemist",
         "convenience", "deli", "gift", "greengrocer", "newsagent", "pet",
         "shoe", "sports", "stationery", "toy", "wine", "bookstore",
         "mobile_phone", "computer", "electronics", "car_parts", "copy",
         "interior_decoration", "lighting", "paint", "appliance", "music")
AMENITY_RE = (r"^(restaurant|cafe|fast_food|hairdresser|beauty_salon|barber|"
              r"car_repair|clinic|dentist|pharmacy|salon|tyres|"
              r"motorcycle_repair|gym|physiotherapist|veterinary|childcare|"
              r"food_court|ice_cream|doctors)$")

# Chains to skip (the pitch must survive contact; chains have HQ sites)
CHAINS = ("pick n pay", "pep", "mugg & bean", "autozone", "clicks", "dis-chem",
          "shoprite", "checkers", "boxer", "usave", "woolworths", "spar",
          "kfc", "mcdonald", "debonairs", "steers", "ocean basket", "nando",
          "roman's pizza", "burger king", "mcdonalds", "game", "makro",
          "builders", "ackermans", "jet", "edgars", "legit", "identity",
          "cell c", "mtn", "vodacom", "telkom", "fNB", "standard bank",
          "absa", "nedbank", "capitec", "cash converters", "cashbuild",
          "spec-savers", "tony & guy", "sheet street", "trueworths",
          "mr price", "picknpay", "checkers", "tops", "cna", "postnet")

SERVICES = {
    "restaurant": ["Lunch & dinner", "Takeaway & delivery", "Group bookings",
                   "Daily specials", "Catering"],
    "cafe": ["Coffee & treats", "Breakfast & lunch", "Takeaway", "Free WiFi",
             "Cakes & pastries"],
    "fast_food": ["Quick meals", "Takeaway", "Delivery", "Combo specials",
                  "Family packs"],
    "hairdresser": ["Haircuts & styling", "Braids & weaves", "Relaxers & treatments",
                    "Kids' cuts", "Events & bridal"],
    "beauty_salon": ["Hair & nails", "Facials & skincare", "Make-up",
                     "Lashes & brows", "Bridal packages"],
    "barber": ["Men's cuts", "Beard trims", "Fades & line-ups", "Kids' cuts",
               "Hot-towel shave"],
    "salon": ["Hair & beauty", "Nails & care", "Waxing", "Kids' styling",
              "Bridal"],
    "car_repair": ["Servicing & repairs", "Diagnostics", "Brakes & suspension",
                   "Battery & tyres", "Roadworthy"],
    "tyres": ["Tyre fitment", "Wheel alignment", "Balancing", "Punctures",
              "Battery"],
    "motorcycle_repair": ["Bike servicing", "Repairs", "Tyres", "Spares",
                          "Roadworthy"],
    "clinic": ["Consultations", "Chronic care", "Minor procedures", "Script renewals",
               "Health checks"],
    "doctors": ["Consultations", "Chronic care", "Check-ups", "Script renewals",
                "Referrals"],
    "dentist": ["Check-ups & cleaning", "Fillings & crowns", "Whitening",
                "Emergency care", "Kids' dentistry"],
    "pharmacy": ["Prescriptions", "Over-the-counter", "Health advice",
                 "Chronic meds", "Wellness"],
    "chemist": ["Prescriptions", "Over-the-counter", "Health advice",
                "Chronic meds", "Wellness"],
    "gym": ["Memberships", "Group classes", "Personal training", "Free weights",
            "Cardio"],
    "physiotherapist": ["Injury rehab", "Sports physio", "Massage", "Dry needling",
                        "Post-op"],
    "veterinary": ["Consultations", "Vaccinations", "Sterilisation", "Emergencies",
                   "Pet care"],
    "bakery": ["Fresh bread", "Cakes & pastries", "Custom orders", "Treats",
               "Events"],
    "butcher": ["Fresh meat", "Braai packs", "Boerewors", "Marinades", "Orders"],
    "default": ["Quality service", "Friendly local team", "Bookings welcome",
                "Competitive prices", "Trusted locally"],
}


def slug(s):
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "business"


def norm_phone(p):
    if not p:
        return None
    d = re.sub(r"[^0-9]", "", p)
    if d.startswith("27") and len(d) >= 11:
        return "+" + d
    if d.startswith("0") and len(d) == 10:
        return "+27" + d[1:]
    if len(d) == 9:
        return "+27" + d
    return None


def is_chain(name):
    n = name.lower()
    return any(c in n for c in CHAINS)


def build_q(lat, lon):
    shop_clauses = "\n".join(
        f'  node["shop"="{s}"](around:{RADIUS},{lat},{lon});' for s in SHOPS)
    amen_clause = f'  node["amenity"~"{AMENITY_RE}"](around:{RADIUS},{lat},{lon});'
    return ("[out:json][timeout:120];\n(\n" + shop_clauses + "\n" + amen_clause +
            "\n);\nout center;")


def fetch(url, q):
    data = urllib.parse.urlencode({"data": q}).encode()
    req = urllib.request.Request(url, data=data,
                                 headers={"User-Agent": "SiteCraftSA/1.0 (thabang@sitecraft.local)"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


def overpass(area, lat, lon):
    q = build_q(lat, lon)
    for m in MIRRORS:
        try:
            return fetch(m, q)
        except Exception as e:
            print(f"  mirror fail {m}: {e}")
            time.sleep(3)
    return None


def category_of(tags):
    if tags.get("amenity") in ("restaurant", "cafe", "fast_food", "hairdresser",
                                "beauty_salon", "barber", "car_repair", "clinic",
                                "doctors", "dentist", "pharmacy", "salon", "tyres",
                                "motorcycle_repair", "gym", "physiotherapist",
                                "veterinary"):
        return tags["amenity"]
    sh = tags.get("shop")
    if sh:
        if sh in ("chemist", "bakery", "butcher"):
            return sh
        return "shop"
    return "default"


def type_label(cat, tags):
    return (tags.get("shop") or tags.get("amenity") or "business").replace("_", " ").title()


def sample_html(name, cat, phone, suburb, city, lat, lon):
    services = SERVICES.get(cat, SERVICES["default"])
    svc = "".join(f"<li>{s}</li>" for s in services)
    tel = "tel:" + re.sub(r"[^0-9]", "", phone)
    wa = ("https://wa.me/" + re.sub(r"[^0-9]", "", phone) +
          "?text=" + urllib.parse.quote(
              f"Hi {name}, I saw the free sample SiteCraft SA built for you. Can we launch it?"))
    maps = (f"https://www.google.com/maps/search/?api=1&query={lat:.5f},{lon:.5f}")
    cat_label = cat.replace("_", " ").title() if cat != "shop" else "Local Business"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(name)} — {html.escape(cat_label)} | SiteCraft SA sample</title>
<meta name="description" content="{html.escape(name)}, {html.escape(cat_label)} serving {html.escape(suburb)}. Call {html.escape(phone)}.">
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
.contact a{{display:block;text-decoration:none;color:#fff;background:#25D366;border-radius:12px;padding:15px;text-align:center;font-weight:700;font-size:16px;margin:14px}}
.contact a.call{{background:#0a7d3e}}
.map a{{display:block;text-align:center;color:#0a7d3e;font-weight:600;padding:10px;text-decoration:none}}
.meta{{color:#555;font-size:14px;margin:6px 14px}}
.foot{{text-align:center;color:#888;font-size:12px;padding:18px}}
</style></head><body>
<div class="banner">FREE sample built by <a href="https://thabs1234.github.io/sitecraft-sa/">SiteCraft SA</a> — no payment needed to claim it.</div>
<div class="hero"><h1>{html.escape(name)}</h1><p>{html.escape(cat_label)} &middot; {html.escape(suburb)}</p></div>
<div class="card"><p style="font-size:15px;color:#333">Welcome to {html.escape(name)}. We serve {html.escape(suburb)} with quality you can trust.
This is a free sample site — your real one can be live in 48 hours.</p></div>
<h2>What we offer</h2><ul>{svc}</ul>
<div class="contact">
  <a class="call" href="{tel}">&#128222; Call {html.escape(phone)}</a>
  <a href="{wa}">&#128172; WhatsApp us</a>
</div>
<h2>Find us</h2><p class="meta">{html.escape(suburb)}, {html.escape(city)}</p>
<div class="map"><a href="{maps}">&#128205; Get directions</a></div>
<div class="foot">Sample by SiteCraft SA &middot; R1,500 setup + R450/mo &middot; wa.me/27745086001</div>
</body></html>"""


def msg1(name, area, sample_url):
    return (f"Hi {name} 👋 I'm Thabang from SiteCraft SA. I noticed you don't have a website, "
            f"so I built you a free sample — no catch, nothing owed: {sample_url} "
            f"Most customers in {area} search Google before they call; right now they find your "
            f"competitors, not you. Want me to walk you through it? (2 min)")


def wa_link(phone, text):
    digits = re.sub(r"[^0-9]", "", phone)
    return f"https://wa.me/{digits}?text=" + urllib.parse.quote(text)


def main():
    os.makedirs(OUT_SAMPLES, exist_ok=True)
    seen = set()
    prospects = []
    for area, (lat, lon) in SUBURBS.items():
        print(f"Pulling {area}...")
        j = overpass(area, lat, lon)
        if not j:
            continue
        for e in j.get("elements", []):
            tags = e.get("tags", {})
            name = tags.get("name")
            if not name:
                continue
            if is_chain(name):
                continue
            if "*" in (tags.get("phone", "") or tags.get("contact:phone", "")):
                continue
            if (tags.get("website") or tags.get("contact:website") or
                    tags.get("facebook") or tags.get("contact:facebook")):
                continue
            phone = norm_phone(tags.get("phone") or tags.get("contact:phone"))
            if not phone:
                continue
            key = (name.lower(), phone)
            if key in seen:
                continue
            seen.add(key)
            lat2 = e.get("lat") or (e.get("center", {}).get("lat"))
            lon2 = e.get("lon") or (e.get("center", {}).get("lon"))
            cat = category_of(tags)
            prospects.append({
                "area": area, "name": name, "cat": cat,
                "phone": phone,
                "lat": lat2 or lat, "lon": lon2 or lon,
            })
        time.sleep(2)
    prospects.sort(key=lambda p: (p["cat"] == "shop" or p["cat"] == "default", p["area"]))
    prospects = prospects[:24]   # clean daily batch
    print(f"\nQualified independent no-website prospects: {len(prospects)}")

    rows = []
    written = 0
    for p in prospects:
        s = slug(p["name"])
        base = s
        i = 2
        while os.path.exists(os.path.join(OUT_SAMPLES, s + ".html")):
            s = f"{base}-{i}"
            i += 1
        city = CITY.get(p["area"], "Gqeberha")
        sample_url = f"https://thabs1234.github.io/sitecraft-sa/samples/pe_el/{s}.html"
        html_txt = sample_html(p["name"], p["cat"], p["phone"], p["area"], city, p["lat"], p["lon"])
        with open(os.path.join(OUT_SAMPLES, s + ".html"), "w", encoding="utf-8") as f:
            f.write(html_txt)
        written += 1
        m1 = msg1(p["name"], p["area"], sample_url)
        rows.append({
            "date": TODAY, "area": p["area"], "name": p["name"],
            "type": type_label(p["cat"], {"shop": p["cat"] if p["cat"] != "shop" else None,
                                          "amenity": p["cat"] if p["cat"] != "shop" else None}),
            "phone": p["phone"], "sample_url": sample_url, "message": m1,
            "wa_link": wa_link(p["phone"], m1), "send_status": "queued",
            "source": "overpass",
        })
    file_exists = os.path.exists(CSV_PATH)
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date", "area", "name", "type", "phone",
                                           "sample_url", "message", "wa_link",
                                           "send_status", "source"])
        if not file_exists:
            w.writeheader()
        for r in rows:
            w.writerow(r)
    with open(os.path.join(ROOT, "tools", "prospect_pe_el_20260817.json"), "w", encoding="utf-8") as f:
        json.dump(prospects, f, ensure_ascii=False, indent=2)

    print(f"Sample sites written: {written} -> samples/pe_el/")
    print(f"Tracker rows appended: {len(rows)}")
    print("By area:", {a: sum(1 for r in rows if r["area"] == a) for a in SUBURBS})
    print("By type:", {t: sum(1 for r in rows if r["type"] == t) for t in sorted({r["type"] for r in rows})})


if __name__ == "__main__":
    main()
