"""Process MondPlan logo: remove edge halo, smart-crop, export multiple sizes.

Source: ~/Desktop/Mondplan.png  (1254x1254 RGBA, 4 corners already alpha=0,
but edge has 1-2px anti-alias halo that looks like a thin white border)

Outputs to /Users/liulu/WorkBuddy/2026-08-21-11-49-03/mondplan/:
  src/brand/full-logo.png          master (halo-removed, content-cropped)
  assets/apple-touch-icon.png      180x180, iOS rounded-rect mask
  assets/apple-touch-icon-167.png  167x167 (iPad)
  assets/apple-touch-icon-152.png  152x152 (iPad)
  assets/favicon-32.png            32x32 favicon fallback
  assets/favicon-16.png            16x16 favicon fallback
  assets/og-logo.png               512x512 transparent logo for OG layouts

The SVG favicon (assets/favicon.svg) is hand-authored (moon + star) and
stays as-is - SVG is not affected by PNG halo issues.
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFilter

SRC = os.path.expanduser("~/Desktop/Mondplan.png")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAND = os.path.join(BASE, "src", "brand")
ASSETS = os.path.join(BASE, "assets")
os.makedirs(BRAND, exist_ok=True)


def remove_halo(img: Image.Image) -> Image.Image:
    """For any near-white opaque pixel in the OUTER 6px RING, set alpha to 0.

    Full image scan would be 1.5M pixels and slow in Python; the halo only
    lives at the edge, so we scan a thin ring. Content is deep blue or gold,
    never near-white, so we never touch the moon/star/ring artwork.
    """
    img = img.convert("RGBA")
    w, h = img.size
    px = img.load()
    RING = 6

    def in_ring(x, y):
        return x < RING or y < RING or x >= w - RING or y >= h - RING

    for y in range(h):
        for x in range(w):
            if not in_ring(x, y):
                continue
            r, g, b, a = px[x, y]
            if a > 200 and r >= 235 and g >= 235 and b >= 235:
                px[x, y] = (0, 0, 0, 0)
    return img


def smart_crop(img: Image.Image, pad: int = 0) -> Image.Image:
    """Crop to bounding box of non-transparent content, with optional padding."""
    bbox = img.getbbox()
    if bbox is None:
        return img
    l, t, r, b = bbox
    if pad:
        l = max(0, l - pad)
        t = max(0, t - pad)
        r = min(img.size[0], r + pad)
        b = min(img.size[1], b + pad)
    return img.crop((l, t, r, b))


def rounded_mask(size: int, radius: int) -> Image.Image:
    """L-mode mask: white inside the rounded rect, black outside.
    iOS App Icon corner radius for size N is roughly N * 0.2237."""
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)
    return mask


def export_resized(src: Image.Image, size: int, out: str, *, rounded: bool = False) -> None:
    """Resize src (RGBA) to size x size with high quality, optionally with
    iOS-style rounded-rect mask. Preserve aspect ratio by fitting into the
    canvas with a small inner padding so the icon doesn't look cramped."""
    canvas_size = size
    inner_pad = int(size * 0.04)  # 4% padding
    content_size = size - 2 * inner_pad
    img = src.resize((content_size, content_size), Image.LANCZOS)
    canvas = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    canvas.paste(img, (inner_pad, inner_pad), img)
    if rounded:
        mask = rounded_mask(canvas_size, int(canvas_size * 0.2237))
        canvas.putalpha(mask)
    canvas.save(out, "PNG", optimize=True)
    print(f"  wrote {os.path.relpath(out, BASE)} ({os.path.getsize(out)} bytes)")


def main() -> None:
    if not os.path.exists(SRC):
        print(f"ERROR: source not found: {SRC}")
        sys.exit(1)

    print(f"=== processing {SRC} ===")
    raw = Image.open(SRC)
    print(f"  source: {raw.size} {raw.mode}")

    # 1. Remove edge halo
    cleaned = remove_halo(raw)
    print("  halo removed")

    # 2. Smart-crop to content bbox (with 1px safety pad)
    cropped = smart_crop(cleaned, pad=1)
    print(f"  cropped to: {cropped.size}")

    # 3. Save master
    master = os.path.join(BRAND, "full-logo.png")
    cropped.save(master, "PNG", optimize=True)
    print(f"  wrote {os.path.relpath(master, BASE)} ({os.path.getsize(master)} bytes)")

    # 4. Export all sizes
    print("=== exporting sizes ===")
    export_resized(cropped, 180, os.path.join(ASSETS, "apple-touch-icon.png"), rounded=True)
    export_resized(cropped, 167, os.path.join(ASSETS, "apple-touch-icon-167.png"), rounded=True)
    export_resized(cropped, 152, os.path.join(ASSETS, "apple-touch-icon-152.png"), rounded=True)
    export_resized(cropped, 512, os.path.join(ASSETS, "og-logo.png"), rounded=False)
    export_resized(cropped, 32, os.path.join(ASSETS, "favicon-32.png"), rounded=False)
    export_resized(cropped, 16, os.path.join(ASSETS, "favicon-16.png"), rounded=False)

    print("done.")


if __name__ == "__main__":
    main()
