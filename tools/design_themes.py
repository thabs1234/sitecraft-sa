#!/usr/bin/env python3
"""SiteCraft SA — DESIGN.md-driven theme engine.

Reads real color tokens from the design templates you installed
(~/design-md/<brand>/DESIGN.md, getdesign variants in ~/design-md-cli)
and maps them onto SiteCraft's single-page sample-site CSS.

This is the bridge between the installed "anti-slop" design toolkit
(taste-skill, impeccable, getdesign/awesome-design-md) and the
working generator (sitecraft/sites/generate_site.py).

No external deps. Pure stdlib.
"""
import os
import re
import json

# Where the installed design templates live (created during setup).
DESIGN_MD_LIB = os.path.expanduser("~/design-md")
DESIGN_MD_CLI = os.path.expanduser("~/design-md-cli")

# Map each SiteCraft business category to the design-brand whose visual
# language fits it best. Tokens are pulled live from the template's DESIGN.md.
# (Brand names must match a directory under ~/design-md/.)
CATEGORY_TO_BRAND = {
    "restaurant":   "airbnb",    # warm, friendly, photography-led, pill radii
    "dentist":      "stripe",     # premium fintech trust, confident purple
    "chemist":      "notion",     # calm, warm-minimal, trustworthy
    "hairdresser":  "claude",     # warm editorial terracotta
    "salon":        "starbucks",  # warm retail green, rounded pills
    "default":      "vercel",     # clean neutral black/white fallback
}


def _read_tokens(brand):
    """Extract real `key: "#hex"` tokens from a brand's DESIGN.md.

    Prefers the full repo copy in ~/design-md, falls back to the getdesign
    CLI variant in ~/design-md-cli. Returns dict of lowercased key -> #hex.
    """
    candidates = [
        os.path.join(DESIGN_MD_LIB, brand, "DESIGN.md"),
        os.path.join(DESIGN_MD_CLI, brand, "DESIGN.md"),
    ]
    text = None
    for path in candidates:
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            break
    if not text:
        return {}
    tokens = {}

    # (1) structured tokens:  primary: "#533afd"  or  accent-blue: '#0099ff'
    for m in re.finditer(r'([a-zA-Z0-9\-]+)\s*:\s*["\']?(#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3})["\']?', text):
        key = m.group(1).lower()
        val = m.group(2).lower()
        if len(val) == 4:
            val = "#" + "".join(c * 2 for c in val[1:])
        tokens.setdefault(key, val)

    # (2) prose tokens:  **Starbucks Green** (... #006241 ...) — the role name
    #     (bolded) carries the meaning; the nearest #hex after it is the value.
    #     Some templates write the hex as (`#006241`) or ( #006241 ) or #006241.
    prose_role_map = {
        "primary": "primary", "brand": "primary", "green": "primary",
        "accent": "primary-active", "green accent": "primary-active",
        "deep": "brand-dark-900", "house green": "brand-dark-900",
        "dark": "brand-dark-900", "house": "brand-dark-900",
        "canvas": "bg", "cream": "bg", "off-white": "bg", "body": "bg",
        "ink": "ink", "on-primary": "on-primary", "white": "on-primary",
    }
    for m in re.finditer(r'\*\*([^*\n]+?)\*\*', text):
        role = m.group(1).strip().lower()
        # search forward up to 160 chars for the first #hex
        window = text[m.end(): m.end() + 160]
        hm = re.search(r'#?[0-9a-fA-F]{6}|#?[0-9a-fA-F]{3}\b', window)
        if not hm:
            continue
        val = hm.group(0).lstrip("#`")
        if len(val) == 3:
            val = "".join(c * 2 for c in val)
        val = "#" + val
        for kw, key in prose_role_map.items():
            if kw in role:
                tokens.setdefault(key, val)
                break

    return tokens


def _contrast_hex(hexcolor):
    """Return '#ffffff' or '#0f172a' depending on luminance of hexcolor."""
    h = hexcolor.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    # perceived luminance
    lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "#ffffff" if lum < 0.6 else "#0f172a"


def get_theme(category):
    """Return a dict of CSS variable values for a SiteCraft category.

    Keys: brand, brand_deep, bg, ink, on_brand, banner_bg
    Falls back to the original teal palette if no template tokens are found.
    """
    brand = CATEGORY_TO_BRAND.get((category or "").lower(), CATEGORY_TO_BRAND["default"])
    t = _read_tokens(brand)

    # Original default palette (kept as safe fallback).
    fallback = {
        "brand": "#0f766e", "brand_deep": "#134e4a", "bg": "#f8fafc",
        "ink": "#0f172a", "on_brand": "#ffffff", "banner_bg": "#0f766e",
        "__source": "fallback",
    }
    if not t:
        fallback["__brand_source"] = brand
        return fallback

    primary = t.get("primary") or t.get("brand") or fallback["brand"]
    # A deeper shade: try *-deep/-dark, else derive by darkening primary.
    deep = (t.get("primary-deep") or t.get("brand-dark-900") or
            t.get("primary-active") or _darken(primary))
    bg = t.get("bg") or t.get("canvas") or t.get("body") or fallback["bg"]
    ink = t.get("ink") or t.get("on-primary") or fallback["ink"]
    on_brand = _contrast_hex(primary)
    return {
        "brand": primary,
        "brand_deep": deep,
        "bg": bg,
        "ink": ink,
        "on_brand": on_brand,
        "banner_bg": primary,
        "__source": brand,          # which DESIGN.md template drove this theme
        "__brand_source": brand,
    }


def _darken(hexcolor, amount=0.78):
    """Multiply RGB by amount to derive a deeper shade. amount<1 darkens."""
    h = hexcolor.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    r, g, b = (max(0, int(c * amount)) for c in (r, g, b))
    return "#%02x%02x%02x" % (r, g, b)


def all_brands():
    """List brand dirs available across both template libraries."""
    out = set()
    for base in (DESIGN_MD_LIB, DESIGN_MD_CLI):
        if os.path.isdir(base):
            out.update(d for d in os.listdir(base)
                       if os.path.isfile(os.path.join(base, d, "DESIGN.md")))
    return sorted(out)


if __name__ == "__main__":
    # Quick self-test: print the theme each category resolves to.
    print("Available brands:", len(all_brands()))
    for cat in ["restaurant", "dentist", "chemist", "hairdresser", "salon", "unknown"]:
        th = get_theme(cat)
        print(f"  {cat:12s} -> brand={th['brand']} source={th['__source']}")
