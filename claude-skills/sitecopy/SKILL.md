---
name: sitecopy
description: "SiteCraft SA: write conversion-focused, human website copy for a local-business sample site (hero, about, services, CTA, contact). Use when building or updating a SiteCraft sample/real site for a named prospect."
---

# sitecopy — local-business website copywriter

## When to use
- You have a real prospect (name, type, area) and need the words for their sample/real site.
- You are fleshing out a `samples/<slug>.html` page or a client's live site.

## Inputs
- `name` — business name
- `type` — salon / restaurant / mechanic / clinic / chemist / gym / etc.
- `area` — suburb / town
- `services` (optional) — if absent, use the defaults below by type

## Service defaults (edit to taste)
- salon/hairdresser/barber/beauty_salon: Haircuts & styling, Braids & weaves, Relaxers & treatments, Kids' cuts, Events & bridal
- restaurant/cafe/fast_food: Lunch & dinner, Takeaway & delivery, Group bookings, Daily specials, Catering
- car_repair/tyres/motorcycle_repair: Servicing & repairs, Diagnostics, Brakes & suspension, Battery & tyres, Roadworthy
- clinic/doctors/dentist: Consultations, Chronic care, Check-ups, Script renewals, Emergency care
- pharmacy/chemist: Prescriptions, Over-the-counter, Health advice, Chronic meds, Wellness
- gym/physiotherapist: Memberships, Group classes, Personal training, Free weights, Cardio
- default: Quality service, Friendly local team, Bookings welcome, Competitive prices, Trusted locally

## Output blocks (plain, warm, South African-friendly, no jargon)
1. **Hero heading** — `{name}` (one line, e.g. "Hair that turns heads in {area}").
2. **Hero sub** — "Your trusted {type} in {area}."
3. **Welcome card** — 1–2 sentences: what they do + the free-sample/live-in-48h line for samples.
4. **What we offer** — bullet list from services above.
5. **Why a real website matters** — 1 sentence: "Most of your customers search Google before they call. A fast mobile site with your number, hours and directions turns that search into a booking — day and night, no ad spend."
6. **Contact** — Call button (tel:), WhatsApp button (wa.me), Get directions (Google Maps).

## Rules
- Keep sentences short. Light emoji only (📞 💬 📍). No fake testimonials, no invented prices.
- Never claim a result you can't back ("3x more customers") — the pitch must survive contact.
- Mirror the live sample style: mobile-first, green brand (#0a7d3e), banner "FREE sample built by SiteCraft SA".
- Output the copy as a small markdown block the site-build skill can drop in, OR full HTML if asked.
