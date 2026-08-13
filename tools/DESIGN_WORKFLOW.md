# SiteCraft SA — Design-Toolkit Workflow

This folder wires the installed "anti-slop" design tools
([taste-skill](https://github.com/Leonxlnx/taste-skill),
[impeccable](https://www.npmjs.com/package/impeccable),
[getdesign](https://www.npmjs.com/package/getdesign) / awesome-design-md,
[img2threejs](https://github.com/img2threejs/img2threejs),
Playwright CLI + Chromium) into the sample-site pipeline.

## What's here

| File | Purpose |
|------|---------|
| `design_themes.py` | Reads **real color tokens** from `~/design-md/<brand>/DESIGN.md` (the 74 templates you installed) and maps them onto SiteCraft's CSS variables per business category. |
| `design_themed_site.py` | Drop-in companion to `sitecraft/sites/generate_site.py`. Same prospect dict in → self-contained themed HTML out. Palette is driven by a DESIGN.md template instead of the hardcoded teal. |
| `preview_site.py` | Playwright **visual preview gate** — renders a generated HTML in real Chromium and saves a full-page PNG. Proves a site actually looks right. |

## Category → template mapping

| Category | DESIGN.md template | Brand color (real token) |
|----------|-------------------|--------------------------|
| restaurant | airbnb | `#ff385c` (Rausch red) |
| dentist | stripe | `#533afd` (Stripe purple) |
| chemist | notion | `#5645d4` |
| hairdresser | claude | `#cc785c` (terracotta) |
| salon | starbucks | `#006241` (Starbucks green) |
| *(fallback)* | vercel | `#171717` |

To change a mapping, edit `CATEGORY_TO_BRAND` in `design_themes.py`.
Any of the 74 brands in `~/design-md/` can be used.

## Generate a themed batch

```bash
cd sitecraft-sa/tools
python design_themed_site.py ../tools/prospects_20260810.json themed_sites
# -> themed_sites/<slug>.html  (one per prospect, themed by category)
```

## Preview a generated site (visual gate)

```bash
cd sitecraft-sa/tools
python preview_site.py themed_sites/a-taste-of-africa.html preview.png
# -> preview.png (full-page screenshot via real Chromium)
```

`preview_site.py` always starts its **own** local HTTP server in the input
file's directory on a fresh port (Playwright blocks `file://`), screenshots,
then tears the server down. It never reuses a foreign server, so it always
captures the right file.

## Design-taste guardrails (run before/after generating)

- `npx skills` → the taste-skill is installed system-wide (Leonxlnx/taste-skill);
  its `design-taste-frontend` / `high-end-visual-design` skills are available to
  Claude Code / Hermes / Codex.
- `impeccable` hooks are installed in `.claude` / `.agents` — run
  `/impeccable init` inside Claude Code to load the design vocab.
- Always eyeball `preview.png` (the visual gate) before sending a sample to a client.

## Requirements

- `python3` (stdlib only — no pip installs for the generators).
- `playwright-cli` on PATH (`npm i -g @playwright/cli`) + Chromium
  (`playwright-cli install-browser chromium`) for `preview_site.py`.
- The design template libraries at `~/design-md/` and `~/design-md-cli/`
  (created by the design-toolkit install step).
