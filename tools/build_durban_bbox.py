#!/usr/bin/env python3
"""SiteCraft SA — Durban bbox top-up (reliable single query, deduped).

One Overpass bounding-box query over eThekwini instead of 10 area queries
(avoids the 429/504 rate limits). Dedupes against the existing tracker so we
don't double-stage the 11 already written, then tops today's batch to 20+.
"""
import urllib.request, urllib.parse, json, time, os, re, csv, html, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_SAMPLES = os.path.join(ROOT, "samples", "durban")
CSV_PATH = os.path.join(ROOT, "outreach", "outreach-tracker.csv")
TODAY = datetime.date(2026, 8, 16).isoformat()

SUBURBS = {
    "Berea": (-29.8579, 31.0218), "Morningside": (-29.8280, 31.0220),
    "Glenwood": (-29.8710, 31.0020), "Umbilo": (-29.8860, 30.9800),
    "Durban North": (-29.8160, 31.0560), "Westville": (-29.8430, 30.9450),
    "Pinetown": (-29.8230, 30.8700), "Kloof": (-29.7900, 30.8100),
    "Chatsworth": (-29.9100, 30.9700), "Umhlanga": (-29.7260, 31.0710),
    "Berea (Upmark)": (-29.8450, 31.0100),
}
# eThekwini bounding box (south,west,north,east)
BBOX = (-30.05, 30.78, -29.60, 31.20)

MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    "https://overpass.openstreetmap.ru/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
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

CHAINS = ("pick n pay", "pep", "mugg & bean", "autozone", "clicks", "dis-chem",
          "shoprite", "checkers", "boxer", "usave", "woolworths", "spar",
          "kfc", "mcdonald", "debonairs", "steers", "ocean basket", "nando",
          "roman's pizza", "burger king", "game", "makro", "builders",
          "ackermans", "jet", "edgars", "legit", "identity", "cell c", "mtn",
          "vodacom", "telkom", "fnb", "standard bank", "absa", "nedbank",
          "capitec", "cash converters", "cashbuild", "spec-savers", "tony & guy",
          "sheet street", "trueworths", "mr price", "tops", "cna", "postnet",
          "house", "cape union", "craighall", "michael angelo")

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
    s = re.sub(r"[^a-z0-9]+", "-", s.lower().strip())
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


def nearest_suburb(lat, lon):
    best, bd = "Durban", 1e9
    for a, (la, lo) in SUBURBS.items():
        d = (lat - la) ** 2 + (lon - lo) ** 2
        if d < bd:
            bd, best = d, a
    return best


def category_of(tags):
    a = tags.get("amenity")
    if a in ("restaurant", "cafe", "fast_food", "hairdresser", "beauty_salon",
             "barber", "car_repair", "clinic", "doctors", "dentist", "pharmacy",
             "salon", "tyres", "motorcycle_repair", "gym", "physiotherapist",
             "veterinary"):
        return a
    sh = tags.get("shop")
    if sh in ("chemist", "bakery", "butcher"):
        return sh
    if sh:
        return "shop"
    return "default"


def type_label(cat, tags):
    return (tags.get("shop") or tags.get("amenity") or "business").replace("_", " ").title()


def sample_html(name, cat, phone, suburb, lat, lon):
    services = SERVICES.get(cat, SERVICES["default"])
    svc = "".join(f"<li>{s}</li>" for s in services)
    tel = "tel:" + re.sub(r"[^0-9]", "", phone)
    wa = ("https://wa.me/" + re.sub(r"[^0-9]", "", phone) +
          "?text=" + urllib.parse.quote(
              f"Hi {name}, I saw the free sample SiteCraft SA built for you. Can we launch it?"))
    maps = f"https://www.google.com/maps/search/?api=1&query={lat:.5f},{lon:.5f}"
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
<h2>Find us</h2><p class="meta">{html.escape(suburb)}, Durban</p>
<div class="map"><a href="{maps}">&#128205; Get directions</a></div>
<div class="foot">Sample by SiteCraft SA &middot; R1,500 setup + R450/mo &middot; wa.me/27745086001</div>
</body></html>"""


def msg1(name, area, sample_url):
    return (f"Hi {name} 👋 I'm Thabang from SiteCraft SA. I noticed you don't have a website, "
            f"so I built you a free sample — no catch, nothing owed: {sample_url} "
            f"Most customers in {area} search Google before they call; right now they find your "
            f"competitors, not you. Want me to walk you through it? (2 min)")


def wa_link(phone, text):
    return "https://wa.me/" + re.sub(r"[^0-9]", "", phone) + "?text=" + urllib.parse.quote(text)


def build_q():
    s, w, n, e = BBOX
    shop_clauses = "\n".join(f'  node["shop"="{x}"]({s},{w},{n},{e});' for x in SHOPS)
    amen = f'  node["amenity"~"{AMENITY_RE}"]({s},{w},{n},{e});'
    return ("[out:json][timeout:180];\n(\n" + shop_clauses + "\n" + amen + "\n);\nout center;")


def fetch(q, tries=4):
    data = urllib.parse.urlencode({"data": q}).encode()
    last = None
    for i in range(tries):
        for m in MIRRORS:
            try:
                req = urllib.request.Request(m, data=data,
                                             headers={"User-Agent": "SiteCraftSA/1.0 (thabang@sitecraft.local)"})
                with urllib.request.urlopen(req, timeout=180) as r:
                    return json.load(r)
            except Exception as ex:
                last = ex
                time.sleep(5 + i * 5)
    raise last


def main():
    os.makedirs(OUT_SAMPLES, exist_ok=True)
    # dedupe set from existing tracker
    seen = set()
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                seen.add((row.get("name", "").lower().strip(),
                          re.sub(r"[^0-9]", "", row.get("phone", ""))))
    # also any durban sample files already written
    for fn in os.listdir(OUT_SAMPLES):
        if fn.endswith(".html"):
            seen.add((fn[:-5].replace("-", " "), ""))

    print("Pulling eThekwini bbox (single query)...")
    j = fetch(build_q())
    els = j.get("elements", [])
    print("elements:", len(els))
    prospects = []
    for e in els:
        tags = e.get("tags", {})
        name = tags.get("name")
        if not name or is_chain(name):
            continue
        if "*" in (tags.get("phone", "") or tags.get("contact:phone", "")):
            continue
        if (tags.get("website") or tags.get("contact:website") or
                tags.get("facebook") or tags.get("contact:facebook")):
            continue
        phone = norm_phone(tags.get("phone") or tags.get("contact:phone"))
        if not phone:
            continue
        if (name.lower().strip(), re.sub(r"[^0-9]", "", phone)) in seen:
            continue
        lat = e.get("lat") or e.get("center", {}).get("lat")
        lon = e.get("lon") or e.get("center", {}).get("lon")
        if lat is None or lon is None:
            continue
        area = tags.get("addr:suburb") or tags.get("addr:city") or nearest_suburb(lat, lon)
        cat = category_of(tags)
        prospects.append({"area": area, "name": name, "cat": cat, "phone": phone,
                          "lat": lat, "lon": lon})
        seen.add((name.lower().strip(), re.sub(r"[^0-9]", "", phone)))
    # prefer concrete categories first
    prospects.sort(key=lambda p: (p["cat"] == "shop" or p["cat"] == "default", p["area"]))
    # top up to ~22 additional (today's goal: 11 already + this >= 12)
    TARGET_ADD = 22
    prospects = prospects[:TARGET_ADD]
    print("New qualified (deduped):", len(prospects))

    rows = []
    for p in prospects:
        s = slug(p["name"])
        base, i = s, 2
        while os.path.exists(os.path.join(OUT_SAMPLES, s + ".html")):
            s = f"{base}-{i}"
            i += 1
        sample_url = f"https://thabs1234.github.io/sitecraft-sa/samples/durban/{s}.html"
        with open(os.path.join(OUT_SAMPLES, s + ".html"), "w", encoding="utf-8") as f:
            f.write(sample_html(p["name"], p["cat"], p["phone"], p["area"], p["lat"], p["lon"]))
        m1 = msg1(p["name"], p["area"], sample_url)
        rows.append({"date": TODAY, "area": p["area"], "name": p["name"],
                     "type": type_label(p["cat"], {"shop": p["cat"] if p["cat"] != "shop" else None,
                                                   "amenity": p["cat"] if p["cat"] != "shop" else None}),
                     "phone": p["phone"], "sample_url": sample_url, "message": m1,
                     "wa_link": wa_link(p["phone"], m1), "send_status": "queued", "source": "overpass"})

    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date", "area", "name", "type", "phone",
                                           "sample_url", "message", "wa_link", "send_status", "source"])
        for r in rows:
            w.writerow(r)

    print(f"Sample sites written: {len(rows)} -> samples/durban/")
    print(f"Tracker rows appended: {len(rows)}")
    print("By area:", {a: sum(1 for r in rows if r['area'] == a) for a in dict.fromkeys(r['area'] for r in rows)})
    print("By type:", {t: sum(1 for r in rows if r['type'] == t) for t in sorted({r['type'] for r in rows})})


if __name__ == "__main__":
    main()
