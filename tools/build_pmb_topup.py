#!/usr/bin/env python3
"""SiteCraft SA — Pietermaritzburg top-up (single bbox query, deduped)."""
import urllib.request, urllib.parse, json, time, os, re, csv, html, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_SAMPLES = os.path.join(ROOT, "samples", "pmb")
CSV_PATH = os.path.join(ROOT, "outreach", "outreach-tracker.csv")
TODAY = datetime.date(2026, 8, 16).isoformat()

BBOX = (-29.70, 30.30, -29.53, 30.48)  # Pietermaritzburg
MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]
SHOPS = ("bakery", "butcher", "clothes", "furniture", "hardware", "florist", "jewelry",
         "optician", "photo", "tailor", "tattoo", "chemist", "convenience", "deli",
         "gift", "greengrocer", "newsagent", "pet", "shoe", "sports", "stationery",
         "toy", "wine", "bookstore", "mobile_phone", "computer", "electronics",
         "car_parts", "copy", "interior_decoration", "lighting", "paint", "appliance", "music")
AMENITY_RE = (r"^(restaurant|cafe|fast_food|hairdresser|beauty_salon|barber|car_repair|"
              r"clinic|dentist|pharmacy|salon|tyres|motorcycle_repair|gym|"
              r"physiotherapist|veterinary|childcare|food_court|ice_cream|doctors)$")
CHAINS = ("pick n pay", "pep", "mugg & bean", "autozone", "clicks", "dis-chem", "shoprite",
          "checkers", "boxer", "usave", "woolworths", "spar", "kfc", "mcdonald", "debonairs",
          "steers", "ocean basket", "nando", "roman's pizza", "burger king", "game", "makro",
          "builders", "ackermans", "jet", "edgars", "legit", "identity", "cell c", "mtn",
          "vodacom", "telkom", "fnb", "standard bank", "absa", "nedbank", "capitec",
          "cash converters", "cashbuild", "spec-savers", "tony & guy", "sheet street",
          "trueworths", "mr price", "tops", "cna", "postnet")

SERVICES = {
    "restaurant": ["Lunch & dinner", "Takeaway & delivery", "Group bookings", "Daily specials", "Catering"],
    "cafe": ["Coffee & treats", "Breakfast & lunch", "Takeaway", "Free WiFi", "Cakes & pastries"],
    "fast_food": ["Quick meals", "Takeaway", "Delivery", "Combo specials", "Family packs"],
    "hairdresser": ["Haircuts & styling", "Braids & weaves", "Relaxers & treatments", "Kids' cuts", "Events & bridal"],
    "beauty_salon": ["Hair & nails", "Facials & skincare", "Make-up", "Lashes & brows", "Bridal packages"],
    "barber": ["Men's cuts", "Beard trims", "Fades & line-ups", "Kids' cuts", "Hot-towel shave"],
    "salon": ["Hair & beauty", "Nails & care", "Waxing", "Kids' styling", "Bridal"],
    "car_repair": ["Servicing & repairs", "Diagnostics", "Brakes & suspension", "Battery & tyres", "Roadworthy"],
    "tyres": ["Tyre fitment", "Wheel alignment", "Balancing", "Punctures", "Battery"],
    "motorcycle_repair": ["Bike servicing", "Repairs", "Tyres", "Spares", "Roadworthy"],
    "clinic": ["Consultations", "Chronic care", "Minor procedures", "Script renewals", "Health checks"],
    "doctors": ["Consultations", "Chronic care", "Check-ups", "Script renewals", "Referrals"],
    "dentist": ["Check-ups & cleaning", "Fillings & crowns", "Whitening", "Emergency care", "Kids' dentistry"],
    "pharmacy": ["Prescriptions", "Over-the-counter", "Health advice", "Chronic meds", "Wellness"],
    "chemist": ["Prescriptions", "Over-the-counter", "Health advice", "Chronic meds", "Wellness"],
    "gym": ["Memberships", "Group classes", "Personal training", "Free weights", "Cardio"],
    "physiotherapist": ["Injury rehab", "Sports physio", "Massage", "Dry needling", "Post-op"],
    "veterinary": ["Consultations", "Vaccinations", "Sterilisation", "Emergencies", "Pet care"],
    "bakery": ["Fresh bread", "Cakes & pastries", "Custom orders", "Treats", "Events"],
    "butcher": ["Fresh meat", "Braai packs", "Boerewors", "Marinades", "Orders"],
    "default": ["Quality service", "Friendly local team", "Bookings welcome", "Competitive prices", "Trusted locally"],
}


def slug(s):
    return (re.sub(r"[^a-z0-9]+", "-", s.lower().strip())).strip("-") or "business"


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


def is_chain(n):
    n = n.lower()
    return any(c in n for c in CHAINS)


def category_of(t):
    a = t.get("amenity")
    if a in ("restaurant", "cafe", "fast_food", "hairdresser", "beauty_salon", "barber",
             "car_repair", "clinic", "doctors", "dentist", "pharmacy", "salon", "tyres",
             "motorcycle_repair", "gym", "physiotherapist", "veterinary"):
        return a
    sh = t.get("shop")
    if sh in ("chemist", "bakery", "butcher"):
        return sh
    if sh:
        return "shop"
    return "default"


def type_label(c, t):
    return (t.get("shop") or t.get("amenity") or "business").replace("_", " ").title()


def sample_html(name, cat, phone, area, lat, lon):
    svc = "".join(f"<li>{s}</li>" for s in SERVICES.get(cat, SERVICES["default"]))
    tel = "tel:" + re.sub(r"[^0-9]", "", phone)
    wa = "https://wa.me/" + re.sub(r"[^0-9]", "", phone) + "?text=" + urllib.parse.quote(
        f"Hi {name}, I saw the free sample SiteCraft SA built for you. Can we launch it?")
    maps = f"https://www.google.com/maps/search/?api=1&query={lat:.5f},{lon:.5f}"
    cl = cat.replace("_", " ").title() if cat != "shop" else "Local Business"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(name)} — {html.escape(cl)} | SiteCraft SA sample</title>
<meta name="description" content="{html.escape(name)}, {html.escape(cl)} serving {html.escape(area)}. Call {html.escape(phone)}.">
<style>
*{{box-sizing:border-box;margin:0;padding:0;font-family:Segoe UI,Roboto,Helvetica,Arial,sans-serif}}
.banner{{background:#0a7d3e;color:#fff;font-size:13px;text-align:center;padding:7px 10px}}
.banner a{{color:#fff;text-decoration:underline}}
.hero{{background:linear-gradient(135deg,#0a7d3e,#13a04f);color:#fff;padding:38px 18px;text-align:center}}
.hero h1{{font-size:27px;margin-bottom:6px}}.hero p{{opacity:.92;font-size:15px}}
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
<div class="hero"><h1>{html.escape(name)}</h1><p>{html.escape(cl)} &middot; {html.escape(area)}</p></div>
<div class="card"><p style="font-size:15px;color:#333">Welcome to {html.escape(name)}. We serve {html.escape(area)} with quality you can trust.
This is a free sample site — your real one can be live in 48 hours.</p></div>
<h2>What we offer</h2><ul>{svc}</ul>
<div class="contact"><a class="call" href="{tel}">&#128222; Call {html.escape(phone)}</a>
<a href="{wa}">&#128172; WhatsApp us</a></div>
<h2>Find us</h2><p class="meta">{html.escape(area)}, Pietermaritzburg</p>
<div class="map"><a href="{maps}">&#128205; Get directions</a></div>
<div class="foot">Sample by SiteCraft SA &middot; R1,500 setup + R450/mo &middot; wa.me/27745086001</div>
</body></html>"""


def msg1(name, area, url):
    return (f"Hi {name} 👋 I'm Thabang from SiteCraft SA. I noticed you don't have a website, "
            f"so I built you a free sample — no catch, nothing owed: {url} "
            f"Most customers in {area} search Google before they call; right now they find your "
            f"competitors, not you. Want me to walk you through it? (2 min)")


def wa_link(phone, text):
    return "https://wa.me/" + re.sub(r"[^0-9]", "", phone) + "?text=" + urllib.parse.quote(text)


def build_q():
    s, w, n, e = BBOX
    sc = "\n".join(f'  node["shop"="{x}"]({s},{w},{n},{e});' for x in SHOPS)
    am = f'  node["amenity"~"{AMENITY_RE}"]({s},{w},{n},{e});'
    return "[out:json][timeout:150];\n(\n" + sc + "\n" + am + "\n);\nout center;"


def fetch(q):
    data = urllib.parse.urlencode({"data": q}).encode()
    last = None
    for i in range(3):
        for m in MIRRORS:
            try:
                req = urllib.request.Request(m, data=data,
                                             headers={"User-Agent": "SiteCraftSA/1.0"})
                with urllib.request.urlopen(req, timeout=150) as r:
                    return json.load(r)
            except Exception as ex:
                last = ex
                time.sleep(4 + i * 4)
    raise last


def main():
    os.makedirs(OUT_SAMPLES, exist_ok=True)
    seen = set()
    if os.path.exists(CSV_PATH):
        for row in csv.DictReader(open(CSV_PATH, encoding="utf-8")):
            seen.add((row.get("name", "").lower().strip(), re.sub(r"[^0-9]", "", row.get("phone", ""))))
    for fn in os.listdir(OUT_SAMPLES):
        if fn.endswith(".html"):
            seen.add((fn[:-5].replace("-", " "), ""))

    print("Pulling Pietermaritzburg bbox...")
    j = fetch(build_q())
    els = j.get("elements", [])
    print("elements:", len(els))
    pros = []
    for e in els:
        t = e.get("tags", {})
        name = t.get("name")
        if not name or is_chain(name):
            continue
        if "*" in (t.get("phone", "") or t.get("contact:phone", "")):
            continue
        if t.get("website") or t.get("contact:website") or t.get("facebook") or t.get("contact:facebook"):
            continue
        phone = norm_phone(t.get("phone") or t.get("contact:phone"))
        if not phone:
            continue
        if (name.lower().strip(), re.sub(r"[^0-9]", "", phone)) in seen:
            continue
        lat = e.get("lat") or e.get("center", {}).get("lat")
        lon = e.get("lon") or e.get("center", {}).get("lon")
        if lat is None or lon is None:
            continue
        area = t.get("addr:suburb") or t.get("addr:city") or "Pietermaritzburg"
        pros.append({"area": area, "name": name, "cat": category_of(t), "phone": phone, "lat": lat, "lon": lon})
        seen.add((name.lower().strip(), re.sub(r"[^0-9]", "", phone)))
    pros.sort(key=lambda p: (p["cat"] == "shop" or p["cat"] == "default", p["area"]))
    pros = pros[:10]
    print("new qualified:", len(pros))
    rows = []
    for p in pros:
        s = slug(p["name"]); base, i = s, 2
        while os.path.exists(os.path.join(OUT_SAMPLES, s + ".html")):
            s = f"{base}-{i}"; i += 1
        url = f"https://thabs1234.github.io/sitecraft-sa/samples/pmb/{s}.html"
        open(os.path.join(OUT_SAMPLES, s + ".html"), "w", encoding="utf-8").write(
            sample_html(p["name"], p["cat"], p["phone"], p["area"], p["lat"], p["lon"]))
        m1 = msg1(p["name"], p["area"], url)
        rows.append({"date": TODAY, "area": p["area"], "name": p["name"],
                     "type": type_label(p["cat"], {"shop": p["cat"] if p["cat"] != "shop" else None,
                                                   "amenity": p["cat"] if p["cat"] != "shop" else None}),
                     "phone": p["phone"], "sample_url": url, "message": m1,
                     "wa_link": wa_link(p["phone"], m1), "send_status": "queued", "source": "overpass"})
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date", "area", "name", "type", "phone", "sample_url",
                                           "message", "wa_link", "send_status", "source"])
        for r in rows:
            w.writerow(r)
    print(f"written: {len(rows)} samples + tracker rows")
    print("by type:", {t: sum(1 for r in rows if r['type'] == t) for t in sorted({r['type'] for r in rows})})


if __name__ == "__main__":
    main()
