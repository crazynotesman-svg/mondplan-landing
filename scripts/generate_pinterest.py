"""Generate 12 Pinterest pins (1000x1500) for the 2026 moon phase calendar.

Each pin shows one month's 4 phases with visual moon icons + dates + times.
Brand mark in corner. Optimized for Pinterest vertical feed.

Output: /assets/pinterest/2026-{01..12}.png
"""
import json
import math
import os
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data", "moon-phases-2026.json")
LOGO = os.path.join(BASE, "src", "brand", "full-logo.png")
OUT_DIR = os.path.join(BASE, "assets", "pinterest")
os.makedirs(OUT_DIR, exist_ok=True)

# Brand palette (matches src/input.css)
BG_TOP = (10, 15, 36)
BG_MID = (17, 26, 58)
BG_BOT = (5, 8, 22)
MOON = (243, 223, 160)
GOLD = (232, 200, 120)
TEXT = (255, 255, 255)
MUTED = (180, 195, 220)
ACCENT = (252, 211, 77)

W, H = 1000, 1500

MONTHS_DE = ["Januar", "Februar", "März", "April", "Mai", "Juni",
             "Juli", "August", "September", "Oktober", "November", "Dezember"]
MONTHS_EN = ["January", "February", "March", "April", "May", "June",
             "July", "August", "September", "October", "November", "December"]


def font(paths, size, bold=False):
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def vertical_gradient(img):
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / (H - 1)
        if t < 0.4:
            k = t / 0.4
            col = tuple(int(BG_TOP[i] + (BG_MID[i] - BG_TOP[i]) * k) for i in range(3))
        else:
            k = (t - 0.4) / 0.6
            col = tuple(int(BG_MID[i] + (BG_BOT[i] - BG_MID[i]) * k) for i in range(3))
        d.line([(0, y), (W, y)], fill=col)


def draw_stars(d, count=70, seed_offset=0):
    import random
    rng = random.Random(1000 + seed_offset)
    for _ in range(count):
        x = rng.uniform(20, W - 20)
        y = rng.uniform(20, H - 20)
        r = rng.choice([1, 1, 1.4, 1.8])
        a = rng.randint(60, 200)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, a))


def moon_polygon(cx, cy, r, phase_p, n=180):
    pts = []
    if phase_p < 0.5:
        for k in range(n + 1):
            a = math.radians(-90 + 180 * k / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        rx = r * math.cos(2 * math.pi * phase_p)
        for k in range(n + 1):
            b = math.radians(90 - 180 * k / n)
            pts.append((cx + rx * math.cos(b), cy + r * math.sin(b)))
    else:
        for k in range(n + 1):
            a = math.radians(-90 - 180 * k / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        rx = r * math.cos(2 * math.pi * (phase_p - 0.5))
        for k in range(n + 1):
            b = math.radians(90 - 180 * k / n)
            pts.append((cx + rx * math.cos(b), cy + r * math.sin(b)))
    return pts


def draw_moon(d, cx, cy, r, phase_p):
    pts = moon_polygon(cx, cy, r, phase_p)
    # halo
    d.ellipse([cx - r - 15, cy - r - 15, cx + r + 15, cy + r + 15], fill=(232, 200, 120, 25))
    d.polygon(pts, fill=MOON)


def phase_p_from_name(name):
    return {
        "new": 0.0,
        "first-quarter": 0.25,
        "full": 0.5,
        "last-quarter": 0.75,
    }.get(name, 0.5)


def make_pin(month_idx: int, events: list, lang: str = "de") -> str:
    """Render a single month pin. Returns the output path."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    vertical_gradient(img)
    d = ImageDraw.Draw(img, "RGBA")
    draw_stars(d, count=80, seed_offset=month_idx * 137)

    # title
    f_h = font(["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Arial Bold.ttf"], 110)
    f_h2 = font(["/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Arial.ttf"], 50)
    f_label = font(["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Arial Bold.ttf"], 38)
    f_date = font(["/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Arial.ttf"], 36)
    f_brand = font(["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Arial Bold.ttf"], 34)

    months = MONTHS_DE if lang == "de" else MONTHS_EN
    month_name = months[month_idx]
    title_top = f"Mondkalender" if lang == "de" else "Moon Calendar"
    title_main = f"{month_name} 2026"
    year_2026 = "Mondphasen 2026" if lang == "de" else "Moon Phases 2026"

    d.text((W // 2, 90), title_top, font=f_h2, fill=GOLD, anchor="mt")
    d.text((W // 2, 150), title_main, font=f_h, fill=TEXT, anchor="mt")
    d.text((W // 2, 270), year_2026, font=f_h2, fill=MUTED, anchor="mt")

    # Phase rows - dynamic count (most months have 4, May 2026 has 5: blue moon)
    phase_names = {
        "de": {"new": "Neumond", "first-quarter": "Erstes Viertel", "full": "Vollmond", "last-quarter": "Letztes Viertel"},
        "en": {"new": "New Moon", "first-quarter": "First Quarter", "full": "Full Moon", "last-quarter": "Last Quarter"},
    }[lang]

    n_events = len(events)
    # Layout: top header 320px, footer 380px -> 800px for rows
    row_top = 350
    row_bot = 1180
    avail = row_bot - row_top
    # leave 10px gap between rows
    if n_events == 0:
        return None
    row_h = avail // n_events
    moon_r = max(38, min(70, int(row_h * 0.28)))

    for i, ev in enumerate(events):
        y = row_top + i * row_h
        # moon visualization on the left
        draw_moon(d, cx=180, cy=y + row_h // 2, r=moon_r, phase_p=phase_p_from_name(ev["phase"]))
        # label and date on the right
        d.text((300, y + 12), phase_names[ev["phase"]], font=f_label, fill=GOLD, anchor="lt")
        utc_dt = datetime.fromisoformat(ev["utc"])
        date_str = utc_dt.strftime("%d.%m.%Y" if lang == "de" else "%b %d, %Y")
        time_str = utc_dt.strftime("%H:%M UTC")
        d.text((300, y + 58), date_str, font=f_date, fill=TEXT, anchor="lt")
        d.text((300, y + 100), time_str, font=f_date, fill=MUTED, anchor="lt")

    # footer
    f_footer = font(["/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Arial.ttf"], 28)
    if lang == "de":
        footer_line1 = "Vollstandiger Kalender:"
        footer_line2 = "mondplan.100ideas.net/de/mondphasen-2026"
    else:
        footer_line1 = "Full calendar:"
        footer_line2 = "mondplan.100ideas.net/moon-phases-2026"
    d.text((W // 2, 1240), footer_line1, font=f_footer, fill=MUTED, anchor="mt")
    d.text((W // 2, 1280), footer_line2, font=f_footer, fill=ACCENT, anchor="mt")

    # CTA pill
    cta_text = "MondPlan App laden" if lang == "de" else "Get MondPlan App"
    pill_w, pill_h = 460, 80
    px = (W - pill_w) // 2
    py = 1340
    d.rounded_rectangle([px, py, px + pill_w, py + pill_h], radius=40, fill=GOLD)
    f_cta = font(["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Arial Bold.ttf"], 32)
    d.text((W // 2, py + pill_h // 2), cta_text, font=f_cta, fill=BG_TOP, anchor="mm")

    # brand mark in top-right corner (small logo)
    if os.path.exists(LOGO):
        logo = Image.open(LOGO).convert("RGBA")
        ls = 110
        logo = logo.resize((ls, ls), Image.LANCZOS)
        img.alpha_composite(logo, (W - ls - 20, 20))

    # bottom brand text
    d.text((40, 1450), "MondPlan  by 100ideas", font=f_brand, fill=MUTED, anchor="lt")

    out = os.path.join(OUT_DIR, f"2026-{month_idx + 1:02d}-{lang}.png")
    img.convert("RGB").save(out, "PNG", optimize=True)
    return out


def main():
    langs = ["de", "en"]
    all_events = json.load(open(DATA))
    # group by month
    by_month = {}
    for ev in all_events:
        ym = ev["utc"][:7]
        by_month.setdefault(ym, []).append(ev)
    for ym in by_month:
        by_month[ym].sort(key=lambda x: x["utc"])

    written = []
    for i in range(12):
        ym = f"2026-{i + 1:02d}"
        events = by_month.get(ym, [])
        for lang in langs:
            path = make_pin(i, events, lang)
            written.append(path)
            print(f"  wrote {os.path.relpath(path, BASE)} ({os.path.getsize(path)} bytes)")

    print(f"\ndone. {len(written)} pins in {OUT_DIR}")


if __name__ == "__main__":
    main()
