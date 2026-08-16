---
name: seo-audit
description: "SiteCraft SA: run a free local-visibility / on-page SEO audit for a local business (or their existing site) and return a scored, plain-English report + the 5 fixes that matter. Use before a pitch or as a paid add-on for a client."
---

# seo-audit — local visibility checker

## When to use
- A prospect HAS a site but it's invisible on Google → audit it, then pitch the fix.
- A client is live → monthly check (part of the R450/mo care).
- Lead-gen hook: "I ran a free visibility check on {name} — here's what's costing you customers."

## Free inputs (no paid tool needed)
- Business name + area
- Their live URL (if any) — fetch with web_extract / curl, read <title>, meta description, h1, mobile viewport, load time (curl -w), does it have WhatsApp/click-to-call, is it on HTTPS.
- Google Business Profile presence — manual check (search "name area"); note if missing.
- Overpass / directory presence — do they appear on Maps listings?

## Audit dimensions (score 0–10 each)
1. **Mobile** — viewport meta present? (most SA searches are mobile)
2. **Speed** — single-file, no heavy images? (target < 2s on 4G)
3. **Local SEO** — Name/Address/Phone consistent, schema.org LocalBusiness JSON-LD present?
4. **GBP** — Google Business Profile claimed & complete (hours, categories, photos)?
5. **Contact** — tap-to-call + WhatsApp button above the fold?
6. **Content** — real services + area keywords on the page (not "Welcome to our website")?

## Output
- A short scored table (dimension | score | one-line fix).
- Total /60 "Local Visibility Score".
- Top 3 fixes ranked by customer impact.
- A closing line: "All of this is included in the R1,500 setup + R450/mo — your sample is already built."

## Reference
- `pdf/security-audit-checklist.html` — companion POPIA/security checklist (Variant A for businesses that already have a site).
- Keep it honest: don't invent a rank you didn't measure. Say "not found on page 1 for 'name area'" only if you actually checked.
