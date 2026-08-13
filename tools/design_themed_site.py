#!/usr/bin/env python3
"""SiteCraft SA — design-themed sample-site generator.

Drop-in companion to sitecraft/sites/generate_site.py. Same prospect dict in,
same self-contained HTML out — but the palette is driven by a real DESIGN.md
template (via design_themes.py) instead of the hardcoded teal.

This lets every niche get a taste-appropriate theme:
  restaurant -> Airbnb warm/photographic
  dentist    -> Stripe premium purple
  chemist    -> Notion warm-minimal
  hairdresser-> Claude editorial terracotta
  salon      -> Starbucks warm green

No external deps. Reuses generate_site.py's slug/whatsapp helpers.
"""
import json
import sys
import html
import urllib.parse
import os

# Import the original generator's pure helpers (slug, whatsapp_link).
GEN_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "sitecraft", "sites")
sys.path.insert(0, os.path.abspath(GEN_DIR))
import generate_site as gen  # noqa: E402

from design_themes import get_theme  # noqa: E402

# Keep the original per-category service copy so the body content is identical.
SERVICES = {
    "dentist": ["Check-ups &amp; cleaning", "Fillings &amp; crowns", "Teeth whitening",
                "Emergency dental care", "Children's dentistry"],
    "restaurant": ["Lunch &amp; dinner", "Takeaway", "Catering", "Group bookings", "Daily specials"],
    "chemist": ["Prescriptions", "Over-the-counter", "Health advice", "Chronic meds", "Wellness products"],
    "hairdresser": ["Haircuts &amp; styling", "Braids &amp; weaves", "Relaxers &amp; treatments",
                    "Kids' cuts", "Events &amp; bridal"],
}


def themed_site_html(p):
    name = p["name"]
    cat = p["category"].replace("_", " ").title()
    phone = p["phone"] or ""
    tel_href = "tel:" + "".join(ch for ch in phone if ch.isdigit())
    wa = gen.whatsapp_link(phone,
        f"Hi {name}, I saw the free sample SiteCraft SA built for you. Can we talk about launching it?")
    addr = p.get("addr") or ""
    suburb = p.get("suburb", "").replace("JHB_", "").replace("PretoriaCentre", "Pretoria")
    maps_q = urllib.parse.quote(f"{name} {suburb}")
    maps = f"https://www.google.com/maps/search/?api=1&query={maps_q}"

    th = get_theme(p["category"])
    source = th.get("__source", "fallback")
    banner = ("Free sample built by SiteCraft SA &mdash; nothing owed. "
              "Live proof you can own in 48h.")

    services = SERVICES.get(cat.lower(),
        ["Quality service", "Friendly local team", "Bookings welcome",
         "Competitive prices", "Trusted in " + suburb])
    svc_html = "".join(f"<li>{s}</li>" for s in services)

    jsonld = json.dumps({
        "@context": "https://schema.org", "@type": "LocalBusiness",
        "name": name, "description": f"{cat} in {suburb}",
        "telephone": phone,
        "address": {"@type": "PostalAddress", "addressLocality": suburb},
        "url": "https://sitecraft.example/" + gen.slug(name),
    }, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(name)} &mdash; {html.escape(cat)} in {html.escape(suburb)}</title>
<meta name="description" content="{html.escape(name)}, {html.escape(cat)} serving {html.escape(suburb)}. Call {html.escape(phone)}.">
<script type="application/ld+json">{jsonld}</script>
<style>
:root{{--brand:{th['brand']};--brand-deep:{th['brand_deep']};--bg:{th['bg']};--ink:{th['ink']};--on-brand:{th['on_brand']};}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:system-ui,Segoe UI,Roboto,Arial,sans-serif;background:var(--bg);color:var(--ink);line-height:1.55}}
.banner{{background:var(--brand);color:var(--on-brand);text-align:center;font-size:.85rem;padding:.5rem 1rem}}
header{{background:linear-gradient(135deg,var(--brand-deep),var(--brand));color:#fff;padding:3.5rem 1.25rem;text-align:center}}
header h1{{font-size:2rem;margin-bottom:.4rem}}
header p{{opacity:.9}}
.wrap{{max-width:880px;margin:0 auto;padding:1.5rem 1.25rem}}
section{{margin:2rem 0}}
h2{{color:var(--brand);font-size:1.4rem;margin-bottom:.75rem}}
ul{{list-style:none;display:grid;grid-template-columns:1fr 1fr;gap:.5rem}}
li{{background:#fff;border-left:4px solid var(--brand);padding:.6rem .8rem;border-radius:6px;box-shadow:0 1px 3px rgba(0,0,0,.06)}}
.cta{{display:flex;flex-wrap:wrap;gap:.75rem;margin-top:1rem}}
a.btn{{display:inline-block;background:var(--brand);color:var(--on-brand);text-decoration:none;padding:.8rem 1.2rem;border-radius:8px;font-weight:600}}
a.btn.alt{{background:#25D366;color:#fff}}
.contact p{{margin:.3rem 0}}
footer{{text-align:center;padding:2rem;color:#64748b;font-size:.85rem}}
@media(max-width:560px){{ul{{grid-template-columns:1fr}}header h1{{font-size:1.6rem}}}}
</style>
</head>
<body>
<div class="banner">{banner}</div>
<header>
  <h1>{html.escape(name)}</h1>
  <p>Your trusted {html.escape(cat.lower())} in {html.escape(suburb)}</p>
</header>
<div class="wrap">
  <section class="cta" style="justify-content:center">
    <a class="btn" href="{tel_href}">&#128222; Call {html.escape(phone)}</a>
    <a class="btn alt" href="{wa}">&#128172; WhatsApp us</a>
    <a class="btn" href="{maps}" target="_blank" rel="noopener">&#128205; Find us</a>
  </section>
  <section>
    <h2>What we offer</h2>
    <ul>{svc_html}</ul>
  </section>
  <section class="contact">
    <h2>Visit or contact us</h2>
    <p>&#128222; <a href="{tel_href}">{html.escape(phone)}</a></p>
    {("<p>&#9993; <a href='mailto:"+html.escape(p['email'])+"'>"+html.escape(p['email'])+"</a></p>") if p.get("email") else ""}
    {(("<p>&#128205; "+html.escape(addr)+", "+html.escape(suburb)+"</p>") if addr else ("<p>&#128205; "+html.escape(suburb)+"</p>"))}
    <p>&#128338; Mon&ndash;Sat, 8:00&ndash;17:00</p>
  </section>
  <section>
    <h2>Why a real website matters</h2>
    <p>Most of your customers search on Google before they call. A fast, mobile site with your number, hours and directions turns that search into a booking &mdash; day and night, with no Ad spend.</p>
  </section>
</div>
<footer>Sample site by SiteCraft SA &bull; {html.escape(name)} owns this &mdash; launch it anytime.
<br><span style="opacity:.6">Theme: {html.escape(source)} DESIGN.md</span></footer>
</body>
</html>"""


if __name__ == "__main__":
    data = json.load(open(sys.argv[1]))
    outdir = sys.argv[2] if len(sys.argv) > 2 else "themed_sites"
    os.makedirs(outdir, exist_ok=True)
    for p in data:
        if p["category"] in ("chemist",) and p["name"] in ("Clicks", "Dis-Chem"):
            continue
        if p["name"].startswith("Tandarts") or "*" in (p["phone"] or ""):
            continue
        th = get_theme(p["category"])
        out = os.path.join(outdir, gen.slug(p["name"]) + ".html")
        open(out, "w", encoding="utf-8").write(themed_site_html(p))
        print(f"wrote {out}  [theme={th.get('__source')}]")
