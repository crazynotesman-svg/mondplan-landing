"""Generate assets/og-image.png (1200x630) for MondPlan.

Same two-disc moon geometry as the interactive widget on the landing page.
Usage: python scripts/generate_og.py
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "og-image.png")

# Palette (matches src/input.css brand tokens)
BG_TOP = (10, 15, 36)      # night-950
BG_MID = (17, 26, 58)      # night-800
BG_BOT = (5, 8, 22)        # darker night
MOON = (243, 223, 160)     # moon-300
TEXT = (255, 255, 255)
MUTED = (148, 163, 184)    # slate-400
ACCENT = (232, 200, 120)   # moon-400


def font(paths, size):
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default(size)


def draw_moon(img, cx, cy, r, phase_p):
    """Draw a moon phase using the same two-disc model as the website widget.

    Two shadow discs share the disc radius, clipped to left/right halves.
    d1 / d2 are horizontal center offsets of the shadow discs relative to cx.
    """
    d1, d2 = 0.0, 0.0
    if phase_p < 0.5:                         # new -> full (waxing)
        d1 = -4 * r * phase_p
        d2 = -4 * r * phase_p
    elif phase_p < 0.75:                      # full -> last quarter (waning)
        d1 = -2 * r + 12 * r * (phase_p - 0.5)
        d2 = -2 * r + 8 * r * (phase_p - 0.5)
    else:                                     # last quarter -> new
        d1 = r - 4 * r * (phase_p - 0.75)
        d2 = 0.0

    moon = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(moon).ellipse([cx - r, cy - r, cx + r, cy + r], fill=MOON + (255,))

    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ds = ImageDraw.Draw(shadow)
    ds.ellipse([cx + d1 - r, cy - r, cx + d1 + r, cy + r], fill=BG_MID + (255,))
    ds.ellipse([cx + d2 - r, cy - r, cx + d2 + r, cy + r], fill=BG_MID + (255,))

    left_mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(left_mask).rectangle([0, 0, cx, H], fill=255)
    right_mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(right_mask).rectangle([cx, 0, W, H], fill=255)

    empty = Image.new("RGBA", img.size, (0, 0, 0, 0))
    moon = Image.alpha_composite(moon, Image.composite(shadow, empty, left_mask))
    moon = Image.alpha_composite(moon, Image.composite(shadow, empty, right_mask))

    img.alpha_composite(moon)


def main():
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

    # Moon (waxing gibbous, ~p=0.32 => about 74% illuminated)
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

    d.text((90, 190), "MondPlan", font=arial_bold, fill=TEXT)
    d.text((94, 310), "Biodynamic Moon Calendar", font=arial, fill=ACCENT)
    d.text((94, 372), "Gardening - Haircut & Beauty - Sleep - Mood", font=arial_small, fill=MUTED)
    d.text((94, 420), "Privacy-first - One-time purchase - iOS", font=arial_small, fill=MUTED)

    img.convert("RGB").save(OUT, "PNG")
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
