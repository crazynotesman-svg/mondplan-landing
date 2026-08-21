"""Generate Open Graph images (1200x630) for MondPlan.

Supports English (og-image.png) and German (og-image-de.png).
The moon uses the same terminator-ellipse model as the website widget.

Usage:
  python scripts/generate_og.py            # generates both languages
  python scripts/generate_og.py en         # English only
  python scripts/generate_og.py de         # German only
"""
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
BRAND = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "brand")

# Palette (matches src/input.css brand tokens)
BG_TOP = (10, 15, 36)      # night-950
BG_MID = (17, 26, 58)      # night-800
BG_BOT = (5, 8, 22)        # darker night
MOON = (243, 223, 160)     # moon-300
TEXT = (255, 255, 255)
MUTED = (148, 163, 184)    # slate-400
ACCENT = (232, 200, 120)   # moon-400

# Localized copy (du form for German, consistent with the site)
COPY = {
    "en": {
        "brand": "MondPlan",
        "subtitle": "Biodynamic Moon Calendar",
        "line1": "Gardening - Haircut & Beauty - Sleep - Mood",
        "line2": "Privacy-first - One-time purchase - iOS",
        "file": "og-image.png",
    },
    "de": {
        "brand": "MondPlan",
        "subtitle": "Biodynamischer Mondkalender",
        "line1": "Gartenbau - Haarschnitt & Schönheit - Schlaf - Stimmung",
        "line2": "Datenschutz zuerst - Einmalkauf - iOS",
        "file": "og-image-de.png",
    },
}


def font(paths, size):
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default(size)


def moon_polygon(cx, cy, r, phase_p, n=180):
    """Illuminated area as a half-disc plus the terminator ellipse arc.

    Matches the moonPath() logic used by the website widget:
    - p in [0, 0.5)  waxing: right half disc + terminator arc (rx = r*cos(2pi*p))
    - p in [0.5, 1)  waning: left half disc + terminator arc (rx = r*cos(2pi*(p-0.5)))
    The terminator arc runs bottom -> top through angle 0 (right side when rx > 0,
    left side when rx < 0), which is the exact SVG sweep-flag equivalent.
    """
    import math
    pts = []
    if phase_p < 0.5:
        # outer arc: right half disc, top (-90 deg) -> bottom (+90 deg)
        for k in range(n + 1):
            a = math.radians(-90 + 180 * k / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        # inner terminator arc: bottom (+90 deg) -> top (-90 deg), through angle 0
        rx = r * math.cos(2 * math.pi * phase_p)
        for k in range(n + 1):
            b = math.radians(90 - 180 * k / n)
            pts.append((cx + rx * math.cos(b), cy + r * math.sin(b)))
    else:
        # outer arc: left half disc, top (-90 deg) -> bottom (-270 deg) via left side
        for k in range(n + 1):
            a = math.radians(-90 - 180 * k / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        # inner terminator arc: bottom (+90 deg) -> top (-90 deg), through angle 0
        rx = r * math.cos(2 * math.pi * (phase_p - 0.5))
        for k in range(n + 1):
            b = math.radians(90 - 180 * k / n)
            pts.append((cx + rx * math.cos(b), cy + r * math.sin(b)))
    return pts


def draw_moon(img, cx, cy, r, phase_p):
    """Draw a moon phase using the same terminator model as the website widget."""
    moon = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(moon).polygon(moon_polygon(cx, cy, r, phase_p), fill=MOON + (255,))
    img.alpha_composite(moon)


def main(lang):
    c = COPY[lang]
    out = os.path.join(ASSETS, c["file"])
    random.seed(6758746304)

    # Vertical gradient background
    img = Image.new("RGBA", (W, H), BG_BOT)
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / (H - 1)
        if t < 0.45:
            k = t / 0.45
            col = tuple(int(BG_TOP[i] + (BG_MID[i] - BG_TOP[i]) * k) for i in range(3))
        else:
            k = (t - 0.45) / 0.55
            col = tuple(int(BG_MID[i] + (BG_BOT[i] - BG_MID[i]) * k) for i in range(3))
        d.line([(0, y), (W, y)], fill=col)

    # Stars (avoid the text zone on the left)
    for _ in range(110):
        x = random.uniform(640, W - 20)
        y = random.uniform(15, H - 15)
        r = random.choice([1, 1, 1.4, 1.8])
        a = random.randint(70, 200)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, a))

    # Moon (waxing gibbous, ~p=0.32 => about 71% illuminated)
    draw_moon(img, cx=920, cy=315, r=205, phase_p=0.32)

    # Soft halo behind the moon
    halo = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(halo).ellipse([920 - 265, 315 - 265, 920 + 265, 315 + 265], fill=(232, 200, 120, 26))
    img.alpha_composite(halo)

    # Typography
    arial_bold = font(["/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                       "/System/Library/Fonts/Arial Bold.ttf"], 96)
    arial = font(["/System/Library/Fonts/Supplemental/Arial.ttf",
                  "/System/Library/Fonts/Arial.ttf"], 34)
    arial_small = font(["/System/Library/Fonts/Supplemental/Arial.ttf",
                        "/System/Library/Fonts/Arial.ttf"], 23)

    d.text((90, 190), c["brand"], font=arial_bold, fill=TEXT)
    d.text((94, 310), c["subtitle"], font=arial, fill=ACCENT)
    d.text((94, 372), c["line1"], font=arial_small, fill=MUTED)
    d.text((94, 420), c["line2"], font=arial_small, fill=MUTED)

    # Brand mark (small logo) - top-right corner, brand reinforcement
    logo_path = os.path.join(BRAND, "full-logo.png")
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        # 96x96 in top-right with 30px margin (logo is square, transparent bg)
        logo_sz = 96
        logo = logo.resize((logo_sz, logo_sz), Image.LANCZOS)
        # place at (W - logo_sz - 30, 30)
        img.alpha_composite(logo, (W - logo_sz - 30, 30))

    img.convert("RGB").save(out, "PNG")
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    langs = sys.argv[1:] if len(sys.argv) > 1 else ["en", "de"]
    for l in langs:
        if l in COPY:
            main(l)
        else:
            print("unknown lang:", l, "(use en/de)")
