---
name: pitch-gen
description: "SiteCraft SA: generate a personalized, ready-to-send WhatsApp (and email) outreach sequence for a local business that has no website. Produces a 5-message follow-up sequence + a wa.me click-to-chat link. Use when given a prospect name/type/area/phone and (optionally) a live sample-site URL."
---

# pitch-gen — SiteCraft SA outreach message generator

## When to use
- You have a real local-business prospect (name, type, area, phone) from OSM/Overpass or a list.
- You want a personalized, human, ban-safe WhatsApp pitch — NOT generic spam.
- You may or may not yet have a live sample site for them.

## Core principle (free-sample-first)
The hook is "I already built it for you" — link a live sample URL. If you don't have a
sample yet, soften to "I'll build you one free" and link the agency page
(https://thabs1234.github.io/sitecraft-sa/). Never send a pitch with no proof.

## Inputs
- `name` (business name), `type` (e.g. salon, mechanic), `area` (suburb/town)
- `phone` (real ZA number, +27 format)  ->  used ONLY for the wa.me link, kept in the local tracker (never published)
- `sample_url` (optional but strongly preferred)

## Output: 5-message sequence (one ask each, human, light emoji)
**MSG 1 (Day 0 — the hook):**
Hi {name} 👋 I'm Thabang from SiteCraft SA. I noticed you don't have a website, so I
built you a free sample — no catch, nothing owed: {sample_url}
Most customers in {area} search Google before they call; right now they find your
competitors, not you. Want me to walk you through it? (2 min)

**MSG 2 (Day 2 — soft nudge + proof):**
Hey {name} — following up on the free site I built: {sample_url}
I do this for local businesses across Joburg, Pretoria and Cape Town. It has your
number, directions, hours and a WhatsApp button so customers reach you from Google.
Still keen to see it live?

**MSG 3 (Day 5 — pre-empt "how much"):**
Hi {name} — if the only thing stopping you is cost, it's smaller than one lost customer
a month: • R1,500 once (your .co.za + domain, live in 48h) • R450/mo (hosting, updates,
WhatsApp button, monthly check). The sample {sample_url} is free to look at either way.

**MSG 4 (Day 8 — scarcity):**
Hey {name} 👋 I'm taking on 5 local businesses this month at the R1,500 setup rate, then
it goes up. Your free sample is ready: {sample_url}. Say "yes" and I'll register the
domain and build it out. No pressure if timing's off.

**MSG 5 (Day 12 — breakup, highest reply rate):**
Hi {name} — I'll stop bugging you after this one 😄 Your free sample stays live: {sample_url}
If a website ever moves up your list, just WhatsApp me. Either way, good luck with {name}!

## wa.me link (ban-safe manual send)
Build: `https://wa.me/{phonenodigits}?text={urlencoded MSG1}`
(phonenodigits = digits only, no +, e.g. 27110698172). Send these MANUALLY from the
WhatsApp Business app — never bulk-automate cold WhatsApp (Meta bans it). 4–5 new
prospects per day, max.

## Reply handling
- "How much?" -> R1,500 + R450/mo, then "Shall I register the domain?"
- "Yes/do it" -> register .co.za (~R120/yr, xneelo/Afrihost), collect R1,500 EFT, build, publish, then R450/mo.
- "Not now" -> "No worries — sample stays live, I'll check back in a month."

## Verification
- [ ] Each message personalized with real name/area (no [BRACKET] left)
- [ ] wa.me link opens with the right pre-filled text
- [ ] Sample URL returns HTTP 200 (if used)
- [ ] Row added to outreach-tracker.csv with send_status=queued
