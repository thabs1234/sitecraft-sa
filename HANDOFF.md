# SiteCraft SA — Lead Engine Handoff (batch 2026-08-10)

## What this is
A zero-cost, repeatable income engine: find SA local businesses with **no website**,
build them a real sample site *before* asking, then close paid deals via WhatsApp.
All prospecting is keyless OpenStreetMap / Overpass — no ad spend, no API cost.

## What was built this batch (verified live)
- **21 raw prospects** pulled from OSM (Johannesburg Fordsburg/CBD + Pretoria Centre).
- **16 qualified** (independent, have phone, no real site): dentists, restaurants, café, hairdresser.
- **16 sample sites** published live on GitHub Pages:
  `https://thabs1234.github.io/sitecraft-sa/samples/<slug>.html`
- **16 outreach packs** (email + proposal text) in `outreach/`.
- **3 proposal PDFs** (dullabh, preis, rhapsodys) in `pdf/`.
- Prospect data: `tools/prospects_20260810.json`.

## The money model
| Item | Price | Notes |
|---|---|---|
| Setup (one-time) | R1,500 | .co.za domain + mobile site + WhatsApp button + Google Business Profile |
| Monthly care | R450/mo | hosting, updates, monthly check |

**Unit economics:** 10 clients = R15,000 setup + R4,500/mo = R54,000/yr recurring, ~R0 cost.
Even 5 clients/month = R7,500 + R2,250/mo.

## How to close (do this next)
1. Open `outreach/emails/<slug>.txt` for the message + the prospect's `wa.me` link.
2. Send **4–5 WhatsApp/day max** (a personal number ban costs more than the leads).
3. Lead with *"I already built your site — free, no catch"* + the live URL.
4. On yes: register `.co.za` (~R120/yr via xneelo/Afrihost), move sample to their domain, collect R1,500.

## Re-run the engine (new city)
```
python prospects/find_prospects.py   # edit AREAS for any SA metro
python sites/generate_site.py prospects/prospects_raw.json
python outreach/build_outreach.py prospects/prospects_raw.json
git add -A && git commit -m batch && git push
```

## Pitfalls (learned)
- Overpass 429s — script already throttles (sleep 4s) + rotates mirrors.
- Skip chains (Clicks, Dis-Chem), masked numbers (`*`), and duplicate "Tandarts" rows.
- Never state a "lost customers" rand figure you didn't compute — the pitch must survive contact.
- WhatsApp blasting risk: cap at 4–5/day on a personal number.

## Files
- Site repo: `thabs1234/sitecraft-sa` (GitHub Pages live)
- Local workspace: `C:/Users/Thabang/sitecraft/`
