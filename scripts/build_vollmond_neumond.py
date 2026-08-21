"""Build Wave 1 SEO pages: Vollmond + Neumond (DE + EN).

Reuses moon-phases-2026.json from data/. Outputs:
  - /de/vollmond-2026.html
  - /de/neumond-2026.html
  - /en/full-moon-2026.html
  - /en/new-moon-2026.html
"""
import json
import os
import re
from datetime import datetime, timezone, timedelta

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE, "data", "moon-phases-2026.json")

CAMPAIGN_LINK = "https://apps.apple.com/app/apple-store/id6758746304?pt=128027998&ct=website_traffic&mt=8"

MONTHS_DE = ["Januar", "Februar", "März", "April", "Mai", "Juni",
             "Juli", "August", "September", "Oktober", "November", "Dezember"]
MONTHS_EN = ["January", "February", "March", "April", "May", "June",
             "July", "August", "September", "October", "November", "December"]

PHASE_LABEL = {
    "de": {"full": "Vollmond", "new": "Neumond", "first-quarter": "Erstes Viertel", "last-quarter": "Letztes Viertel"},
    "en": {"full": "Full Moon", "new": "New Moon", "first-quarter": "First Quarter", "last-quarter": "Last Quarter"},
}

# Traditional full moon names (Northern Hemisphere, Anglo-Saxon + Farmer's Almanac)
FULL_MOON_NAMES_EN = [
    "Wolf Moon",       # January
    "Snow Moon",       # February
    "Worm Moon",       # March
    "Pink Moon",       # April
    "Flower Moon",     # May
    "Strawberry Moon", # June
    "Buck Moon",       # July
    "Sturgeon Moon",   # August
    "Harvest Moon",    # September
    "Hunter's Moon",   # October
    "Beaver Moon",     # November
    "Cold Moon",       # December
]

# German traditional names (less codified; we provide the most common equivalents)
FULL_MOON_NAMES_DE = [
    "Wolfsmond",       # January
    "Schneemond",      # February
    "Wurmmond",        # March
    "Pinkmond",        # April
    "Blumenmond",      # May
    "Erdbeermond",     # June
    "Bockmond",        # July
    "Störmond",        # August
    "Erntemond",       # September
    "Jägermond",       # October
    "Bibermond",       # November
    "Kältemond",       # December
]

PAGE_CONFIG = {
    "vollmond": {
        "de": {
            "url": "https://mondplan.100ideas.net/de/vollmond-2026.html",
            "de_url": "https://mondplan.100ideas.net/de/vollmond-2026.html",
            "en_url": "https://mondplan.100ideas.net/en/full-moon-2026.html",
            "title": "Vollmond 2026 - Alle Termine, Mondnamen & Bedeutungen",
            "h1": "Vollmond 2026",
            "subtitle": "Vollmondkalender mit Daten",
            "desc": "Alle 13 Vollmonde 2026 mit exakten Daten (UTC und MEZ/MESZ), traditionellen Namen (Wolfsmond, Erntemond, ...) und Einfluss auf Schlaf, Garten und Haarschnitt.",
            "filter": "full",
            "phase_label": "Vollmond",
            "phase_label_plural": "Vollmonde",
            "intro": "Dreizehn Vollmonde gibt es 2026, weil der Mai zwei Vollmonde hat (der zweite wird umgangssprachlich 'Blauer Mond' genannt). Die Zeitangaben sind nach Jean Meeus berechnet (Genauigkeit &plusmn;1-2 Minuten) und gegen die NASA-Datenbank verifiziert. CET = Winterzeit (UTC+1), CEST = Sommerzeit (UTC+2).",
            "tradition_section_title": "Traditionelle Vollmondnamen",
            "tradition_intro_de": "Die zwölf traditionellen Namen stammen aus nordamerikanischen Ureinwohner- und Bauernalmanach-Traditionen und beschreiben jahreszeitliche Phänomene.",
            "effects_title": "Was bedeutet der Vollmond?",
            "faq_json": [
                {"q": "Wann ist der nächste Vollmond 2026?", "a": "Der erste Vollmond 2026 ist am 3. Januar um 11:04 MEZ. Es folgen zwölf weitere Vollmonde - einer pro Monat, plus ein zweiter am 31. Mai (Blauer Mond)."},
                {"q": "Was ist ein Blauer Mond?", "a": "Als Blauer Mond bezeichnet man den zweiten Vollmond innerhalb eines Kalendermonats. 2026 tritt dieses Ereignis am 31. Mai ein."},
                {"q": "Wie genau sind diese Zeitangaben?", "a": "Die Daten werden mit dem Standard-Algorithmus aus Jean Meeus 'Astronomical Algorithms' (Kapitel 49) berechnet. Die Genauigkeit betragt plus/minus 1-2 Minuten gegenuber den tatsachlichen astronomischen Ereignissen."},
                {"q": "Beeinflusst der Vollmond den Schlaf?", "a": "Mehrere Studien (u.a. Cajochen et al., 2013) zeigen einen statistisch signifikanten Zusammenhang zwischen Vollmond und verminderter Schlafqualitat - die Effekte sind allerdings individuell sehr unterschiedlich."},
            ],
        },
        "en": {
            "url": "https://mondplan.100ideas.net/en/full-moon-2026.html",
            "de_url": "https://mondplan.100ideas.net/de/vollmond-2026.html",
            "en_url": "https://mondplan.100ideas.net/en/full-moon-2026.html",
            "title": "Full Moon 2026 - All Dates, Names & Meanings",
            "h1": "Full Moon 2026",
            "subtitle": "Full Moon Calendar with Dates",
            "desc": "All 13 full moons of 2026 with exact UTC and CET/CEST times, traditional names (Wolf Moon, Harvest Moon, ...), and effects on sleep, gardening and haircuts.",
            "filter": "full",
            "phase_label": "Full Moon",
            "phase_label_plural": "Full Moons",
            "intro": "Thirteen full moons occur in 2026, with May having two (the second is colloquially called a 'Blue Moon'). Times are computed with Jean Meeus' algorithm (accuracy +/-1-2 minutes) and cross-checked against the NASA database. CET = winter (UTC+1), CEST = summer (UTC+2).",
            "tradition_section_title": "Traditional Full Moon Names",
            "tradition_intro_en": "The twelve traditional names come from Native American and Farmers' Almanac traditions and describe seasonal phenomena.",
            "effects_title": "What does the full moon mean?",
            "faq_json": [
                {"q": "When is the next full moon in 2026?", "a": "The first full moon of 2026 is on January 3 at 11:04 CET. Twelve more follow - one per month, plus a second on May 31 (Blue Moon)."},
                {"q": "What is a Blue Moon?", "a": "A Blue Moon is the second full moon within a calendar month. In 2026 this occurs on May 31."},
                {"q": "How accurate are these times?", "a": "Times are calculated with the standard algorithm from Jean Meeus' 'Astronomical Algorithms' (chapter 49). Accuracy is plus/minus 1-2 minutes against actual astronomical events."},
                {"q": "Does the full moon affect sleep?", "a": "Several studies (e.g. Cajochen et al., 2013) show a statistically significant association between full moon and reduced sleep quality, though effects vary widely between individuals."},
            ],
        },
    },
    "neumond": {
        "de": {
            "url": "https://mondplan.100ideas.net/de/neumond-2026.html",
            "de_url": "https://mondplan.100ideas.net/de/neumond-2026.html",
            "en_url": "https://mondplan.100ideas.net/en/new-moon-2026.html",
            "title": "Neumond 2026 - Alle Termine, Einfluss & Rituale",
            "h1": "Neumond 2026",
            "subtitle": "Neumondkalender mit Daten",
            "desc": "Alle 12 Neumonde 2026 mit exakten Daten (UTC und MEZ/MESZ), traditioneller Bedeutung und Einfluss auf Aussaat, Vorsatze und Schlaf.",
            "filter": "new",
            "phase_label": "Neumond",
            "phase_label_plural": "Neumonde",
            "intro": "Zwolf Neumonde gibt es 2026. Wahrend des Neumonds steht der Mond zwischen Erde und Sonne - die beleuchtete Seite ist von uns abgewandt, der Mond ist am Nachthimmel unsichtbar. Die Zeitangaben sind nach Jean Meeus berechnet (Genauigkeit &plusmn;1-2 Minuten).",
            "tradition_section_title": "Neumond-Bedeutung in verschiedenen Traditionen",
            "tradition_intro_de": "In vielen Kulturen gilt der Neumond als Zeit des Neuanfangs - ideale Zeit fur Aussaat, neue Projekte, Rituale oder die Formulierung von Vorsatzen.",
            "effects_title": "Was bedeutet der Neumond?",
            "faq_json": [
                {"q": "Wann ist der nachste Neumond 2026?", "a": "Der erste Neumond 2026 ist am 18. Januar um 20:54 MEZ. Es folgen elf weitere Neumonde, einer pro Monat."},
                {"q": "Warum ist der Neumond unsichtbar?", "a": "Beim Neumond steht der Mond zwischen Erde und Sonne. Die beleuchtete Halbkugel des Mondes ist von der Erde abgewandt, sodass wir den Mond am Nachthimmel nicht sehen konnen."},
                {"q": "Eignet sich der Neumond zum Gartnern?", "a": "In der biodynamischen Landwirtschaft gilt der Neumond als Ruhephase - gunstig fur Bodenbearbeitung, Unkraut jaten und Planung der nachsten Aussaat."},
                {"q": "Wie genau sind diese Zeitangaben?", "a": "Die Daten werden mit dem Standard-Algorithmus aus Jean Meeus 'Astronomical Algorithms' (Kapitel 49) berechnet. Genauigkeit plus/minus 1-2 Minuten."},
            ],
        },
        "en": {
            "url": "https://mondplan.100ideas.net/en/new-moon-2026.html",
            "de_url": "https://mondplan.100ideas.net/de/neumond-2026.html",
            "en_url": "https://mondplan.100ideas.net/en/new-moon-2026.html",
            "title": "New Moon 2026 - All Dates, Influence & Rituals",
            "h1": "New Moon 2026",
            "subtitle": "New Moon Calendar with Dates",
            "desc": "All 12 new moons of 2026 with exact UTC and CET/CEST times, traditional meanings and effects on gardening, intentions and sleep.",
            "filter": "new",
            "phase_label": "New Moon",
            "phase_label_plural": "New Moons",
            "intro": "Twelve new moons occur in 2026. During a new moon, the moon stands between Earth and Sun - the lit side faces away from us and the moon is invisible in the night sky. Times are computed with Jean Meeus' algorithm (accuracy +/-1-2 minutes).",
            "tradition_section_title": "New Moon Meaning Across Traditions",
            "tradition_intro_en": "In many cultures the new moon is a time of new beginnings - ideal for sowing, new projects, rituals or setting intentions.",
            "effects_title": "What does the new moon mean?",
            "faq_json": [
                {"q": "When is the next new moon in 2026?", "a": "The first new moon of 2026 is on January 18 at 20:54 CET. Eleven more follow - one per month."},
                {"q": "Why is the new moon invisible?", "a": "During a new moon, the moon stands between Earth and Sun. The lit hemisphere faces away from Earth, so we cannot see the moon in the night sky."},
                {"q": "Is the new moon good for gardening?", "a": "In biodynamic farming, the new moon is a rest phase - favorable for soil work, weeding and planning the next sowing."},
                {"q": "How accurate are these times?", "a": "Times are calculated with the standard algorithm from Jean Meeus' 'Astronomical Algorithms' (chapter 49). Accuracy plus/minus 1-2 minutes."},
            ],
        },
    },
}


def to_cet(utc_str):
    """UTC ISO -> CET/CEST string (e.g. '11:04 CET' or '13:54 CEST')."""
    # parse as naive UTC then attach tz for comparison
    dt_naive = datetime.fromisoformat(utc_str)
    dt_utc = dt_naive.replace(tzinfo=timezone.utc)
    # CEST = UTC+2 (last Sunday of March to last Sunday of October)
    year = dt_utc.year
    mar_last = datetime(year, 3, 31)
    while mar_last.weekday() != 6:
        mar_last -= timedelta(days=1)
    oct_last = datetime(year, 10, 31)
    while oct_last.weekday() != 6:
        oct_last -= timedelta(days=1)
    is_summer = (mar_last.replace(hour=1, tzinfo=timezone.utc)
                 <= dt_utc
                 < oct_last.replace(hour=1, tzinfo=timezone.utc))
    offset = 2 if is_summer else 1
    local = dt_naive + timedelta(hours=offset)
    return f"{local.strftime('%H:%M')} {'CEST' if is_summer else 'CET'}"


def build_table_html(events, lang):
    """Build the 12-month phase table HTML."""
    months = MONTHS_DE if lang == "de" else MONTHS_EN
    table_label = {
        "de": {"phase": "Phase", "date": "Datum", "utc": "UTC", "local": "MEZ/MESZ"},
        "en": {"phase": "Phase", "date": "Date", "utc": "UTC", "local": "CET/CEST"},
    }[lang]
    label = {"de": "Vollmond", "en": "Full Moon"} if events[0]["phase"] == "full" else {"de": "Neumond", "en": "New Moon"}
    # group by month
    by_month = {}
    for ev in events:
        ym = ev["utc"][:7]
        by_month.setdefault(ym, []).append(ev)
    by_month = {k: sorted(v, key=lambda x: x["utc"]) for k, v in by_month.items()}
    blocks = []
    for ym in sorted(by_month):
        idx = int(ym.split("-")[1]) - 1
        month_name = f"{months[idx]} {ym[:4]}"
        rows = []
        for ev in by_month[ym]:
            utc_dt = datetime.fromisoformat(ev["utc"])
            date_str = utc_dt.strftime("%d.%m.%Y" if lang == "de" else "%B %d")
            rows.append(
                f'<tr class="border-b border-white/5 last:border-0">'
                f'<td class="py-2.5 pr-4 font-medium text-slate-200">{label[lang]}</td>'
                f'<td class="py-2.5 pr-4 whitespace-nowrap text-slate-300">{date_str}</td>'
                f'<td class="py-2.5 pr-4 text-slate-400">{utc_dt.strftime("%H:%M UTC")}</td>'
                f'<td class="py-2.5 text-slate-300 whitespace-nowrap">{to_cet(ev["utc"])}</td>'
                f'</tr>'
            )
        block = (
            f'<div class="rounded-2xl border border-white/10 bg-night-900/70 p-6">'
            f'<h3 class="text-lg font-semibold text-white">{month_name}</h3>'
            f'<div class="mt-4 overflow-x-auto">'
            f'<table class="w-full min-w-[520px] text-sm">'
            f'<thead><tr class="border-b border-white/10 text-left text-slate-500">'
            f'<th class="pb-2 pr-4 font-medium">{table_label["phase"]}</th>'
            f'<th class="pb-2 pr-4 font-medium">{table_label["date"]}</th>'
            f'<th class="pb-2 pr-4 font-medium">{table_label["utc"]}</th>'
            f'<th class="pb-2 font-medium">{table_label["local"]}</th>'
            f'</tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div></div>'
        )
        blocks.append(block)
    return "\n".join(blocks)


def build_tradition_html(events, page_type, lang):
    """Traditional names (full moon only) or generic new moon list."""
    if page_type == "neumond":
        # no codified names, but we add a list of all 12 dates
        label = {"de": "Neumond 2026 - Ubersicht", "en": "New Moon 2026 - Overview"}
        intro = {
            "de": "Alle zwolf Neumonde des Jahres auf einen Blick. Die Daten sind exakt nach Jean Meeus berechnet.",
            "en": "All twelve new moons of the year at a glance. Times are exact per Jean Meeus.",
        }[lang]
        months = MONTHS_DE if lang == "de" else MONTHS_EN
        items = []
        for ev in events:
            utc_dt = datetime.fromisoformat(ev["utc"])
            date_str = utc_dt.strftime("%d. %B %Y" if lang == "de" else "%B %d, %Y")
            items.append(
                f'<li class="flex items-baseline gap-3 border-b border-white/5 pb-2 last:border-0">'
                f'<span class="w-6 h-6 rounded-full bg-night-800 flex-shrink-0" aria-hidden="true"></span>'
                f'<span class="font-medium text-slate-200">{date_str}</span>'
                f'<span class="text-slate-500">- {utc_dt.strftime("%H:%M UTC")} / {to_cet(ev["utc"])}</span>'
                f'</li>'
            )
        return (
            f'<section class="border-y border-white/5 bg-night-900/60" aria-labelledby="traditions-title">'
            f'<div class="mx-auto max-w-6xl px-5 py-14">'
            f'<h2 id="traditions-title" class="text-2xl font-bold tracking-tight text-white">{label[lang]}</h2>'
            f'<p class="mt-3 max-w-2xl text-slate-400">{intro}</p>'
            f'<ul class="mt-8 max-w-2xl space-y-1 text-sm">{"".join(items)}</ul>'
            f'</div></section>'
        )
    # full moon: 12 traditional names
    months = MONTHS_DE if lang == "de" else MONTHS_EN
    names = FULL_MOON_NAMES_DE if lang == "de" else FULL_MOON_NAMES_EN
    cards = []
    for i, m in enumerate(months):
        cards.append(
            f'<li class="rounded-2xl border border-white/10 bg-night-950/60 p-5">'
            f'<p class="text-xs uppercase tracking-widest text-moon-400">{m}</p>'
            f'<p class="mt-1 text-lg font-semibold text-white">{names[i]}</p>'
            f'</li>'
        )
    intro = PAGE_CONFIG["vollmond"][lang]["tradition_intro_de"] if lang == "de" else PAGE_CONFIG["vollmond"][lang]["tradition_intro_en"]
    title = PAGE_CONFIG["vollmond"][lang]["tradition_section_title"]
    return (
        f'<section class="border-y border-white/5 bg-night-900/60" aria-labelledby="traditions-title">'
        f'<div class="mx-auto max-w-6xl px-5 py-14">'
        f'<h2 id="traditions-title" class="text-2xl font-bold tracking-tight text-white">{title}</h2>'
        f'<p class="mt-3 max-w-2xl text-slate-400">{intro}</p>'
        f'<ol class="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">{"".join(cards)}</ol>'
        f'</div></section>'
    )


def build_events_json_ld(events, page_url, lang):
    """Build ItemList JSON-LD of all phase events for GEO."""
    items = []
    for ev in events:
        utc_dt = datetime.fromisoformat(ev["utc"])
        items.append({
            "@type": "Event",
            "name": f"{PHASE_LABEL[lang][ev['phase']]} - {utc_dt.strftime('%B %Y')}",
            "startDate": ev["utc"],
            "eventStatus": "https://schema.org/EventScheduled",
            "eventAttendanceMode": "https://schema.org/OnlineEventAttendanceMode",
        })
    return {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "2026 phase calendar",
        "numberOfItems": len(items),
        "itemListElement": items,
    }


def build_faq_json_ld(faqs):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": faq["q"], "acceptedAnswer": {"@type": "Answer", "text": faq["a"]}}
            for faq in faqs
        ],
    }


def build_article_json_ld(cfg, lang, page_url, events):
    return {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": cfg["h1"],
        "description": cfg["desc"],
        "url": page_url,
        "inLanguage": "de" if lang == "de" else "en",
        "datePublished": "2026-08-21",
        "dateModified": "2026-08-21",
        "author": {"@type": "Organization", "name": "100ideas", "url": "https://100ideas.net"},
        "publisher": {
            "@type": "Organization",
            "name": "100ideas",
            "logo": {"@type": "ImageObject", "url": "https://mondplan.100ideas.net/assets/favicon.svg"},
        },
        "about": [
            {"@type": "Thing", "name": cfg["phase_label"]},
            {"@type": "Thing", "name": "Astronomical Algorithms by Jean Meeus"},
        ],
        "citation": [
            "Meeus, Jean. Astronomical Algorithms (2nd ed.). Willmann-Bell, 1998. Chapter 49.",
            "NASA Five Millennium Canon of Solar Eclipses / Lunar Eclipses",
        ],
    }


def build_breadcrumb_json_ld(cfg, lang, page_url, page_type):
    en_label = {"vollmond": "Full Moon 2026", "neumond": "New Moon 2026"}[page_type]
    de_label = {"vollmond": "Vollmond 2026", "neumond": "Neumond 2026"}[page_type]
    home_label = "Home" if lang == "en" else "Startseite"
    home_url = "https://mondplan.100ideas.net/" if lang == "en" else "https://mondplan.100ideas.net/de/"
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": home_label, "item": home_url},
            {"@type": "ListItem", "position": 2, "name": en_label if lang == "en" else de_label, "item": page_url},
        ],
    }


def build_app_json_ld(lang):
    en = {
        "@context": "https://schema.org", "@type": "MobileApplication",
        "name": "MondPlan - Biodynamic Moon Calendar",
        "operatingSystem": "iOS 16.0 or later",
        "applicationCategory": "LifestyleApplication",
        "offers": {"@type": "Offer", "price": "0.00", "priceCurrency": "USD"},
        "url": "https://mondplan.100ideas.net/en/full-moon-2026.html" if lang == "en" else "https://mondplan.100ideas.net/de/vollmond-2026.html",
        "sameAs": ["https://apps.apple.com/app/id6758746304"],
    }
    de = {
        "@context": "https://schema.org", "@type": "MobileApplication",
        "name": "MondPlan - Biodynamischer Mondkalender",
        "operatingSystem": "iOS 16.0 oder hoher",
        "applicationCategory": "LifestyleApplication",
        "offers": {"@type": "Offer", "price": "0.00", "priceCurrency": "EUR"},
        "url": "https://mondplan.100ideas.net/de/vollmond-2026.html" if lang == "de" and "vollmond" in str(en.get("url","")) else ("https://mondplan.100ideas.net/de/neumond-2026.html" if lang == "de" else "https://mondplan.100ideas.net/en/new-moon-2026.html"),
        "sameAs": ["https://apps.apple.com/app/id6758746304"],
    }
    return de if lang == "de" else en


def page_html(page_type, lang, cfg, all_events, filtered_events):
    nav_label = "EN" if lang == "de" else "DE"
    nav_url = cfg["en_url"] if lang == "de" else cfg["de_url"]
    hreflang_url_en = cfg["en_url"]
    hreflang_url_de = cfg["de_url"]

    table_html = build_table_html(filtered_events, lang)
    tradition_html = build_tradition_html(filtered_events, page_type, lang)
    events_ld = build_events_json_ld(filtered_events, cfg["url"], lang)
    faq_ld = build_faq_json_ld(cfg["faq_json"])
    article_ld = build_article_json_ld(cfg, lang, cfg["url"], filtered_events)
    breadcrumb_ld = build_breadcrumb_json_ld(cfg, lang, cfg["url"], page_type)
    app_ld = build_app_json_ld(lang)

    # FAQ HTML body (same as JSON-LD for accordion consistency)
    faq_accordion = []
    for faq in cfg["faq_json"]:
        faq_accordion.append(
            f'<details class="group rounded-2xl border border-white/10 bg-night-900/70 p-5">'
            f'<summary class="flex cursor-pointer items-center justify-between gap-4 text-base font-medium text-white">'
            f'<span>{faq["q"]}</span>'
            f'<svg class="h-5 w-5 flex-shrink-0 text-moon-400 transition group-open:rotate-180" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>'
            f'</summary>'
            f'<p class="mt-3 text-sm leading-relaxed text-slate-300">{faq["a"]}</p>'
            f'</details>'
        )
    faq_accordion_html = "".join(faq_accordion)

    cta_text = "MondPlan App laden" if lang == "de" else "Get MondPlan App"
    nav_about = "Uber" if lang == "de" else "About"
    nav_privacy = "Datenschutz" if lang == "de" else "Privacy"
    nav_support = "Support" if lang == "de" else "Support"
    nav_phases = "Mondphasen 2026" if lang == "de" else "Moon Phases 2026"
    related_links_title = "Weitere Mondkalender" if lang == "de" else "More Moon Calendars"

    # ---- Correct relative URLs. Pages live in a subdirectory:
    #   de/ pages: /de/vollmond-2026.html etc (siblings in /de/)
    #   en/ pages: /en/full-moon-2026.html etc (siblings in /en/)
    # Root pages (index, privacy, support, moon-phases) need ../ when
    # referenced from en/ or de/ subdirectories.
    home_url = "index.html" if lang == "de" else "../index.html"
    privacy_url = "privacy.html" if lang == "de" else "../privacy.html"
    support_url = "support.html" if lang == "de" else "../support.html"
    phases_url = "mondphasen-2026.html" if lang == "de" else "../moon-phases-2026.html"
    features_url = "index.html#features" if lang == "de" else "../index.html#features"
    # cross-language page URL (from de -> en sibling, or en -> de sibling)
    cross_lang_url = cfg["en_url"] if lang == "de" else cfg["de_url"]
    # related pages: same-language counterparts
    if page_type == "vollmond":
        related_other_url = "neumond-2026.html" if lang == "de" else "new-moon-2026.html"
        related_other_label = "Neumond 2026" if lang == "de" else "New Moon 2026"
        related_other_desc = "Alle 12 Neumonde, Daten, Bedeutung." if lang == "de" else "All 12 new moons, dates, meaning."
    else:
        related_other_url = "vollmond-2026.html" if lang == "de" else "full-moon-2026.html"
        related_other_label = "Vollmond 2026" if lang == "de" else "Full Moon 2026"
        related_other_desc = "Alle 13 Vollmonde, Namen, Daten." if lang == "de" else "All 13 full moons, names, dates."
    # Garten page is DE-only; link it from both languages via its absolute path
    garten_url = "../de/mondkalender-garten-2026.html" if lang == "en" else "mondkalender-garten-2026.html"
    garten_label = "Mondkalender Garten 2026" if lang == "de" else "Moon Gardening 2026"
    garten_desc = "Aussaat, Ernte, Bodenpflege nach Mond." if lang == "de" else "Sowing, harvest, soil work by moon."
    faq_title = "Haufige Fragen" if lang == "de" else "Frequently Asked Questions"
    effects = {
        "de": {
            "vollmond": [
                ("Schlaf", "Studien zeigen einen statistisch signifikanten Zusammenhang zwischen Vollmond und verminderter Schlafqualitat. Individuelle Effekte variieren stark."),
                ("Garten", "Traditionell gilt der Vollmond als gunstige Zeit fur die Ernte von Wurzelgemuse und Obst - die Pflanzensafte sollen dann oben sein."),
                ("Haarschnitt", "Viele Friseure empfehlen den Vollmond fur kraftvolle Schnitte, die schneller nachwachsen."),
            ],
            "neumond": [
                ("Schlaf", "Einige Menschen berichten uber tieferen Schlaf in Neumond-Nachten - wissenschaftlich ist dies weniger untersucht als der Vollmond-Effekt."),
                ("Garten", "Der Neumond gilt als Ruhephase - gunstig fur Bodenbearbeitung, Unkraut jaten und Aussaatplanung."),
                ("Rituale", "Der Neumond ist in vielen Kulturen die klassische Zeit fur Neuanfange, Intentionen setzen und neue Projekte starten."),
            ],
        },
        "en": {
            "vollmond": [
                ("Sleep", "Studies show a statistically significant association between full moon and reduced sleep quality. Individual effects vary widely."),
                ("Gardening", "Traditionally, the full moon is favorable for harvesting root vegetables and fruit - plant sap is said to rise."),
                ("Haircuts", "Many hairdressers recommend the full moon for powerful cuts that grow back faster."),
            ],
            "neumond": [
                ("Sleep", "Some people report deeper sleep during new moon nights - this is less scientifically studied than the full moon effect."),
                ("Gardening", "The new moon is a rest phase - favorable for soil work, weeding and sowing planning."),
                ("Rituals", "In many cultures, the new moon is the classic time for new beginnings, setting intentions and starting new projects."),
            ],
        },
    }[lang][page_type]

    intro_eyebrow = "Mondkalender" if lang == "de" else "Moon Calendar"
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <title>{cfg['title']}</title>
  <meta name="description" content="{cfg['desc']}">
  <meta name="apple-itunes-app" content="app-id=6758746304">
  <link rel="canonical" href="{cfg['url']}">
  <meta name="theme-color" content="#0a0f24">
  <meta name="author" content="100ideas">

  <link rel="alternate" hreflang="en" href="{hreflang_url_en}">
  <link rel="alternate" hreflang="de" href="{hreflang_url_de}">
  <link rel="alternate" hreflang="x-default" href="{hreflang_url_en}">

  <meta property="og:type" content="article">
  <meta property="og:site_name" content="MondPlan">
  <meta property="og:title" content="{cfg['title']}">
  <meta property="og:description" content="{cfg['desc']}">
  <meta property="og:url" content="{cfg['url']}">
  <meta property="og:image" content="https://mondplan.100ideas.net/assets/og-image-de.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:locale" content="{'de_DE' if lang == 'de' else 'en_US'}">
  <meta property="og:locale:alternate" content="{'en_US' if lang == 'de' else 'de_DE'}">

  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{cfg['title']}">
  <meta name="twitter:description" content="{cfg['desc']}">
  <meta name="twitter:image" content="https://mondplan.100ideas.net/assets/og-image-de.png">

  <link rel="icon" type="image/svg+xml" href="../assets/favicon.svg?v=3">
  <link rel="apple-touch-icon" href="../assets/apple-touch-icon.png?v=3">
  <link rel="stylesheet" href="../assets/tailwind.css?v=3">

  <script type="application/ld+json">
  {json.dumps(article_ld, ensure_ascii=False, indent=2)}
  </script>
  <script type="application/ld+json">
  {json.dumps(breadcrumb_ld, ensure_ascii=False, indent=2)}
  </script>
  <script type="application/ld+json">
  {json.dumps(events_ld, ensure_ascii=False, indent=2)}
  </script>
  <script type="application/ld+json">
  {json.dumps(faq_ld, ensure_ascii=False, indent=2)}
  </script>
  <script type="application/ld+json">
  {json.dumps(app_ld, ensure_ascii=False, indent=2)}
  </script>
</head>
<body class="bg-night-950 text-slate-100 antialiased">

  <header class="sticky top-0 z-40 border-b border-white/5 bg-night-950/80 backdrop-blur-md">
    <nav class="mx-auto flex max-w-6xl items-center justify-between px-5 py-4" aria-label="Main">
      <a href="{home_url}" class="flex items-center gap-2 text-base font-semibold text-white">
        <span aria-hidden="true">&#9790;</span>
        MondPlan
      </a>
      <div class="hidden items-center gap-7 text-sm text-slate-300 md:flex">
        <a href="{phases_url}" class="transition hover:text-moon-300">{nav_phases}</a>
        <a href="{features_url}" class="transition hover:text-moon-300">{'Features' if lang == 'en' else 'Funktionen'}</a>
        <a href="#faq" class="transition hover:text-moon-300">FAQ</a>
      </div>
      <div class="flex items-center gap-3">
        <a href="{cross_lang_url}" class="text-sm text-slate-400 transition hover:text-moon-300" rel="alternate" hreflang="{'en' if lang == 'de' else 'de'}">{nav_label}</a>
        <a href="{CAMPAIGN_LINK}" class="rounded-full bg-moon-300 px-4 py-2 text-sm font-semibold text-night-950 transition hover:bg-moon-200">{cta_text}</a>
      </div>
    </nav>
  </header>

  <main>
    <section class="starfield relative overflow-hidden" aria-labelledby="page-title">
      <div class="pointer-events-none absolute inset-0 bg-gradient-to-b from-night-900/40 via-transparent to-night-950" aria-hidden="true"></div>
      <div class="mx-auto max-w-6xl px-5 py-16 md:py-20">
        <p class="text-sm font-semibold uppercase tracking-widest text-moon-400">{intro_eyebrow} - 2026</p>
        <h1 id="page-title" class="mt-3 text-3xl font-bold tracking-tight text-white md:text-4xl lg:text-5xl">
          {cfg['h1']}
        </h1>
        <p class="mt-5 max-w-2xl text-lg leading-relaxed text-slate-300">
          {cfg['intro']}
        </p>
        <div class="mt-6 flex flex-wrap gap-x-6 gap-y-2 text-sm text-slate-400">
          <span class="flex items-center gap-1.5">
            <svg class="h-4 w-4 text-moon-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>
            {len(filtered_events)} {cfg['phase_label_plural']} {'im Jahr' if lang == 'de' else 'in 2026'}
          </span>
          <span class="flex items-center gap-1.5">
            <svg class="h-4 w-4 text-moon-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>
            {'Berechnet nach Jean Meeus, &plusmn;1-2 min' if lang == 'de' else 'Calculated with Jean Meeus, +/-1-2 min'}
          </span>
        </div>
      </div>
    </section>

    {tradition_html}

    <section class="mx-auto max-w-6xl px-5 py-14" aria-labelledby="table-title">
      <div class="max-w-2xl">
        <h2 id="table-title" class="text-2xl font-bold tracking-tight text-white">{cfg['phase_label']}-{'Termine 2026' if lang == 'de' else ' dates 2026'}</h2>
        <p class="mt-3 text-slate-400">
          {'Exakte Zeitpunkte in UTC und MEZ/MESZ (Winter UTC+1, Sommer UTC+2).' if lang == 'de' else 'Exact instants in UTC and CET/CEST (winter UTC+1, summer UTC+2).'}
        </p>
      </div>

      <div class="mt-8 space-y-6">
        {table_html}
      </div>
    </section>

    <section class="border-y border-white/5 bg-night-900/60" aria-labelledby="effects-title">
      <div class="mx-auto max-w-6xl px-5 py-14">
        <h2 id="effects-title" class="text-2xl font-bold tracking-tight text-white">{cfg['effects_title']}</h2>
        <div class="mt-8 grid gap-6 md:grid-cols-3">
          {''.join(
            f'<article class="rounded-2xl border border-white/10 bg-night-950/60 p-6">'
            f'<h3 class="text-lg font-semibold text-moon-300">{e[0]}</h3>'
            f'<p class="mt-2 text-sm leading-relaxed text-slate-300">{e[1]}</p>'
            f'</article>'
            for e in effects
          )}
        </div>
      </div>
    </section>

    <section class="mx-auto max-w-3xl px-5 py-14" aria-labelledby="faq-title" id="faq">
      <h2 id="faq-title" class="text-2xl font-bold tracking-tight text-white">{faq_title}</h2>
      <div class="mt-8 space-y-3">
        {faq_accordion_html}
      </div>
    </section>

    <section class="border-t border-white/5 bg-night-900/60">
      <div class="mx-auto max-w-6xl px-5 py-14">
        <h2 class="text-2xl font-bold tracking-tight text-white">{related_links_title}</h2>
        <ul class="mt-6 grid gap-4 sm:grid-cols-2">
          <li><a href="{phases_url}" class="block rounded-2xl border border-white/10 bg-night-950/60 p-5 transition hover:border-moon-400/30">
            <p class="text-sm font-semibold text-white">{nav_phases}</p>
            <p class="mt-1 text-xs text-slate-400">{'Vollstandiger Mondkalender mit allen 4 Phasen pro Monat.' if lang == 'de' else 'Complete lunar calendar with all 4 phases per month.'}</p>
          </a></li>
          <li><a href="{related_other_url}" class="block rounded-2xl border border-white/10 bg-night-950/60 p-5 transition hover:border-moon-400/30">
            <p class="text-sm font-semibold text-white">{related_other_label}</p>
            <p class="mt-1 text-xs text-slate-400">{related_other_desc}</p>
          </a></li>
          <li><a href="{garten_url}" class="block rounded-2xl border border-white/10 bg-night-950/60 p-5 transition hover:border-moon-400/30">
            <p class="text-sm font-semibold text-white">{garten_label}</p>
            <p class="mt-1 text-xs text-slate-400">{garten_desc}</p>
          </a></li>
          <li><a href="{home_url}" class="block rounded-2xl border border-white/10 bg-night-950/60 p-5 transition hover:border-moon-400/30">
            <p class="text-sm font-semibold text-white">{'MondPlan Startseite' if lang == 'de' else 'MondPlan home'}</p>
            <p class="mt-1 text-xs text-slate-400">{'Der biodynamische Mondkalender fur iOS.' if lang == 'de' else 'The biodynamic moon calendar for iOS.'}</p>
          </a></li>
        </ul>
      </div>
    </section>

    <section class="mx-auto max-w-4xl px-5 py-20 text-center">
      <h2 class="text-3xl font-bold tracking-tight text-white">{cta_text}</h2>
      <p class="mt-3 text-slate-300">{'MondPlan bringt diesen Kalender in die Hosentasche - mit Erinnerungen, Widgets und allen Funktionen.' if lang == 'de' else 'MondPlan puts this calendar in your pocket - with reminders, widgets and all features.'}</p>
      <a href="{CAMPAIGN_LINK}" class="mt-8 inline-block rounded-full bg-moon-300 px-8 py-3 text-base font-semibold text-night-950 transition hover:bg-moon-200">{cta_text}</a>
    </section>
  </main>

  <footer class="border-t border-white/5 bg-night-900/60">
    <div class="mx-auto max-w-6xl px-5 py-10 flex flex-col items-start justify-between gap-6 sm:flex-row sm:items-center">
      <p class="text-sm text-slate-500">&copy; 2026 100ideas. Alle Daten nach Jean Meeus &copy; 1998.</p>
      <nav class="flex flex-col gap-3 text-sm text-slate-400 sm:flex-row sm:items-center sm:gap-8" aria-label="Footer navigation">
        <a href="{home_url}" class="transition hover:text-moon-300">{'Startseite' if lang == 'de' else 'Home'}</a>
        <a href="{privacy_url}" class="transition hover:text-moon-300">{nav_privacy}</a>
        <a href="{support_url}" class="transition hover:text-moon-300">{nav_support}</a>
        <a href="{phases_url}" class="transition hover:text-moon-300">{nav_phases}</a>
        <a href="{CAMPAIGN_LINK}" class="transition hover:text-moon-300">App Store</a>
      </nav>
    </div>
  </footer>
</body>
</html>
"""


def main():
    all_events = json.load(open(DATA_FILE))
    written = []

    for page_type in ["vollmond", "neumond"]:
        for lang in ["de", "en"]:
            cfg = PAGE_CONFIG[page_type][lang]
            filtered = [ev for ev in all_events if ev["phase"] == cfg["filter"]]
            filtered = sorted(filtered, key=lambda x: x["utc"])
            html = page_html(page_type, lang, cfg, all_events, filtered)
            if page_type == "vollmond":
                rel = f"de/vollmond-2026.html" if lang == "de" else "en/full-moon-2026.html"
            else:
                rel = f"de/neumond-2026.html" if lang == "de" else "en/new-moon-2026.html"
            out = os.path.join(BASE, rel)
            os.makedirs(os.path.dirname(out), exist_ok=True)
            open(out, "w", encoding="utf-8").write(html)
            written.append(out)
            print(f"  wrote {os.path.relpath(out, BASE)} ({os.path.getsize(out)} bytes) - {len(filtered)} events")

    print(f"\ndone. {len(written)} pages.")


if __name__ == "__main__":
    main()
