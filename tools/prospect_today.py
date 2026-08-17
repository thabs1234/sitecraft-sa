#!/usr/bin/env python3
"""SiteCraft SA daily prospector (cron, Day 4+).
Pulls REAL no-website businesses WITH a phone from OpenStreetMap Overpass in
fresh SA township areas, de-dupes, and writes prospect_today.json.
Falls back to existing township/wa data only if Overpass yields <20.
Stdlib only. No API key. Sends a real User-Agent (Overpass rejects the default).
"""
import urllib.request, urllib.parse, json, time, sys, re, os

AREAS = {
    "Soweto":   (-26.2485, 27.8540),
    "Mamelodi": (-25.7300, 28.3500),
    "Tembisa":  (-25.9800, 28.2300),
}
RADIUS = 4000

MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
]

# business tags likely to lack a site but have a phone
AMENITY_RE = r'^(restaurant|cafe|fast_food|hairdresser|beauty_salon|barber|car_repair|clinic|dentist|pharmacy|salon|tyres|motorcycle_repair)$'

def build_q(lat, lon):
    clauses = []
    for tag in (f'node["shop"](around:{RADIUS},{lat},{lon});',
                f'way["shop"](around:{RADIUS},{lat},{lon});',
                f'node["amenity"~"{AMENITY_RE}"](around:{RADIUS},{lat},{lon});',
                f'way["amenity"~"{AMENITY_RE}"](around:{RADIUS},{lat},{lon});'):
        clauses.append(tag)
    return "[out:json][timeout:90];(\n" + "\n".join(clauses) + "\n);out center;"

def norm_phone(p):
    if not p:
        return None
    d = re.sub(r"[^\d]", "", p)
    if d.startswith("27") and len(d) >= 11:
        return "+" + d
    if d.startswith("0") and len(d) == 10:
        return "+27" + d[1:]
    if len(d) == 9:  # missing leading 0
        return "+27" + d
    return None

def fetch(url, q):
    data = urllib.parse.urlencode({"data": q}).encode()
    req = urllib.request.Request(url, data=data, headers={"User-Agent": "SiteCraftSA/1.0 (thabang@sitecraft.local)"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.load(r)

def overpass(area, lat, lon):
    q = build_q(lat, lon)
    last = None
    for m in MIRRORS:
        try:
            j = fetch(m, q)
            return j
        except Exception as e:
            last = e
            time.sleep(2)
    print(f"  ! Overpass failed for {area}: {last}", file=sys.stderr)
    return None

def collect():
    seen = {}
    for area, (lat, lon) in AREAS.items():
        print(f"Pulling {area} ...", file=sys.stderr)
        j = overpass(area, lat, lon)
        if not j:
            continue
        for el in j.get("elements", []):
            t = el.get("tags", {})
            name = t.get("name")
            if not name:
                continue
            phone = norm_phone(t.get("phone") or t.get("contact:phone"))
            if not phone:
                continue
            web = t.get("website") or t.get("contact:website") or t.get("url")
            if web:  # skip those that already have a site
                continue
            typ = (t.get("shop") or t.get("amenity") or "").replace("_", " ").title()
            key = (name.lower(), phone)
            if key in seen:
                continue
            cen = el.get("center") or {}
            lat2 = el.get("lat") or cen.get("lat")
            lon2 = el.get("lon") or cen.get("lon")
            addr = ", ".join(v for v in [t.get("addr:street"), t.get("addr:suburb"), t.get("addr:city")] if v)
            seen[key] = {
                "area": area, "name": name, "type": typ,
                "phone": phone, "addr": addr,
                "lat": lat2, "lon": lon2,
            }
        time.sleep(1.5)
    return list(seen.values())

if __name__ == "__main__":
    out = collect()
    print(f"OVERPASS NEW PROSPECTS (no-site + phone): {len(out)}", file=sys.stderr)
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "prospect_today.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    for p in out[:5]:
        print(f"  {p['area']:9} {p['name'][:28]:28} {p['type'][:12]:12} {p['phone']}", file=sys.stderr)
    print(f"WROTE prospect_today.json ({len(out)} prospects)", file=sys.stderr)
