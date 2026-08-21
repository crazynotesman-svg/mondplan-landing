"""Insert a visible FAQ section into moon-phases-2026.html (EN) and
de/mondphasen-2026.html (DE) right before the CTA section.

The questions/answers are pulled from each page's own FAQPage JSON-LD,
so the visible accordion and the structured data stay 100% in sync.
Native <details>/<summary> is used (no JS needed) - same pattern as the
Wave 1/2 content pages.

Usage: python scripts/add_faq_section.py
"""
import json
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = ["moon-phases-2026.html", os.path.join("de", "mondphasen-2026.html")]

FAQ_HEADING = {
    "en": "Frequently asked questions",
    "de": "Häufige Fragen",
}

FAQ_SUB = {
    "en": "Quick answers about the 2026 moon phases, the synodic month and how the calendar is computed.",
    "de": "Kurze Antworten zu den Mondphasen 2026, dem synodischen Monat und der Berechnung des Kalenders.",
}


def extract_faq_page(html):
    blocks = re.findall(
        r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', html, re.DOTALL
    )
    for b in blocks:
        try:
            d = json.loads(b)
        except Exception:
            continue
        if isinstance(d, dict) and d.get("@type") == "FAQPage":
            return d.get("mainEntity", [])
    return []


def build_faq_html(qas, lang):
    heading = FAQ_HEADING[lang]
    sub = FAQ_SUB[lang]
    items = []
    for qa in qas:
        q = qa.get("name", "").replace('"', "&quot;")
        a = qa.get("acceptedAnswer", {}).get("text", "").replace('"', "&quot;")
        items.append(
            '<details class="group rounded-2xl border border-white/10 bg-night-900/70 p-5">'
            '<summary class="flex cursor-pointer items-center justify-between gap-4 text-base font-medium text-white">'
            f"<span>{q}</span>"
            '<svg class="h-5 w-5 flex-shrink-0 text-moon-400 transition group-open:rotate-180" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>'
            "</summary>"
            f'<p class="mt-3 text-sm leading-relaxed text-slate-300">{a}</p>'
            "</details>"
        )
    section = (
        '<section class="border-y border-white/5 bg-night-900/60" aria-labelledby="faq-title" id="faq">'
        '<div class="mx-auto max-w-3xl px-5 py-14">'
        f'<h2 id="faq-title" class="text-2xl font-bold tracking-tight text-white">{heading}</h2>'
        f'<p class="mt-3 text-slate-400">{sub}</p>'
        f'<div class="mt-8 space-y-3">{"".join(items)}</div>'
        "</div>"
        "</section>"
    )
    return section


def main():
    for rel in PAGES:
        path = os.path.join(BASE, rel)
        html = open(path, encoding="utf-8").read()
        lang = "de" if rel.startswith("de") else "en"
        qas = extract_faq_page(html)
        if not qas:
            print(f"  !! {rel}: no FAQPage JSON-LD found, skipping")
            continue
        faq_html = build_faq_html(qas, lang)

        # insert before the CTA section (identified by its comment or the CTA h2)
        anchor = "<!-- ============ CTA ============ -->"
        if anchor not in html:
            # fallback: insert before the closing </main>
            anchor = "</main>"
            faq_html = faq_html + "\n\n  "
        if anchor in html:
            html = html.replace(anchor, faq_html + "\n\n    " + anchor, 1)
            open(path, "w", encoding="utf-8").write(html)
            print(f"  {rel}: inserted FAQ section ({len(qas)} items)")
        else:
            print(f"  !! {rel}: anchor not found, skipping")

    # verify
    print()
    for rel in PAGES:
        html = open(os.path.join(BASE, rel), encoding="utf-8").read()
        visible = html.count("<details")
        qas = extract_faq_page(html)
        print(f"  verify {rel}: visible details={visible}  jsonld questions={len(qas)}  match={visible == len(qas)}")


if __name__ == "__main__":
    main()
