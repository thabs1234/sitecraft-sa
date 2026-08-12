#!/usr/bin/env python3
"""SiteCraft SA prospector v2: pull local businesses that ALREADY have a website
(but likely a weak/vulnerable one) from OpenStreetMap Overpass (keyless).

These are the Variant A "security audit" targets — businesses whose site may
fail the 4 security checks (POPIA liability angle). Include their site URL."""
import json, sys, time, urllib.request

OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]
UA = "SiteCraftProspector/2.0 (local lead-gen)"

AREAS = {
    "JHB_Fordsburg": (-26.22, 27.99, -26.18, 28.04),
    "JHB_CBD":       (-26.21, 28.01, -26.15, 28.07),
    "PretoriaCentre":(-25.78, 28.16, -25.71, 28.24),
}

CATS = [
    'node["shop"="hairdresser"]', 'node["shop"="beauty"]',
    'node["amenity"="restaurant"]', 'node["amenity"="hairdresser"]',
    'node["shop"="chemist"]', 'node["craft"="painter"]',
    'node["shop"="car_repair"]', 'node["amenity"="dentist"]',
    'node["office"="tax_advisor"]',
]

def build_query(area):
    s, w, n, e = area
    lines = []
    for cat in CATS:
        lines.append(cat + "(" + str(s) + "," + str(w) + "," + str(n) + "," + str(e) + ");")
    inner = "\n".join(lines)
    return "[out:json][timeout:90];(" + inner + ");out center;"

def query_overpass(q):
    for ep in OVERPASS_ENDPOINTS:
        try:
            req = urllib.request.Request(ep, data=q.encode(),
                headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read().decode())
        except Exception as ex:
            print("  endpoint " + ep + " failed: " + str(ex), file=sys.stderr)
            time.sleep(3)
    return None

def clean_phone(p):
    if not p: return None
    if "*" in p: return None
    nums = [x.strip() for x in p.replace(";", ",").split(",")]
    for x in nums:
        digits = "".join(ch for ch in x if ch.isdigit())
        if len(digits) >= 9:
            return x
    return None

def site_of(tags):
    for k in ("website", "contact:website", "url"):
        v = tags.get(k)
        if v and "facebook" not in v.lower():
            return v
    return None

def main():
    all_rows, seen = [], set()
    for name, area in AREAS.items():
        print("Querying " + name + " ...", file=sys.stderr)
        data = query_overpass(build_query(area))
        if not data:
            print("  " + name + ": no data", file=sys.stderr); continue
        for el in data.get("elements", []):
            tags = el.get("tags", {})
            bname = tags.get("name")
            if not bname: continue
            site = site_of(tags)
            if not site: continue            # INVERTED: only WITH website
            phone = clean_phone(tags.get("phone") or tags.get("contact:phone") or tags.get("tel"))
            email = tags.get("email") or tags.get("contact:email")
            if not (phone or email): continue
            lat = el.get("lat") or el.get("center", {}).get("lat")
            key = (bname.lower(), lat)
            if key in seen: continue
            seen.add(key)
            lon = el.get("lon") or el.get("center", {}).get("lon")
            row = {"name": bname, "phone": phone, "email": email,
                   "website": site, "area": name,
                   "lat": lat, "lon": lon,
                   "suburb": tags.get("addr:suburb") or tags.get("addr:city") or ""}
            all_rows.append(row)
    with open("prospects/prospects_with_sites.json", "w", encoding="utf-8") as f:
        json.dump(all_rows, f, ensure_ascii=False, indent=1)
    print("Wrote " + str(len(all_rows)) + " with-site prospects -> prospects/prospects_with_sites.json")

if __name__ == "__main__":
    main()
