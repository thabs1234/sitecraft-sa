---
name: site-build
description: "SiteCraft SA: build a self-contained, mobile-first sample website (single HTML file) for a local business with a WhatsApp button, tap-to-call and directions. Use to produce the 'free sample' that powers the pitch-gen hook."
---

# site-build — one-file mobile sample site

## When to use
- You have a prospect (name, type, area, phone) and need the live "free sample" URL.
- Output is dropped in `samples/<area or slug>/<slug>.html` and pushed to GitHub Pages.

## Inputs
- `name`, `type`, `area`, `phone` (+ optional lat/lon for the directions link)

## Hard requirements (the sample must survive contact)
- Single self-contained `.html` (inline CSS, no external requests) → loads on 4G in <2s.
- Mobile-first (`<meta name="viewport" content="width=device-width,initial-scale=1">`).
- Brand green `#0a7d3e` hero + banner: "FREE sample built by SiteCraft SA — no payment needed to claim it."
- **Above the fold**: Call (`tel:`) + WhatsApp (`wa.me/<digits>?text=...`) + Get directions (Google Maps).
- Sections: hero (name + type·area), welcome card, "What we offer" (services by type — see sitecopy), contact, "Why a real website matters", footer (R1,500 setup + R450/mo · wa.me/27745086001).
- `schema.org` LocalBusiness JSON-LD with name, telephone, addressLocality.
- `<title>` + meta description with name + type + area (on-page SEO).

## Generator
Reuse `tools/design_themed_site.py` (DESIGN.md themes) or the compact
`sample_html()` pattern in `tools/build_durban_batch.py`. Both are stdlib-only.
Slug = lowercased name, non-alphanumerics → `-`.

## After build
1. Open in a browser / Playwright to confirm mobile render + buttons work (preview gate).
2. `git add samples/... && git commit && git push` → URL live on GitHub Pages.
3. Feed the live URL into pitch-gen so MSG1 says "I already built it for you".

## Rule
The sample is the proof. Never pitch a business whose sample 404s — verify the URL
returns 200 before the message leaves your hands.
