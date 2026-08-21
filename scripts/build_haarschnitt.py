"""Build the German Haarschnitt-nach-dem-Mond 2026 page.

Reuses moon-phases-2026.json from data/. Output:
  - /de/haarschnitt-nach-dem-mond-2026.html
"""
import json
import os
from datetime import datetime, timezone, timedelta

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE, "data", "moon-phases-2026.json")

CAMPAIGN_LINK = "https://apps.apple.com/app/apple-store/id6758746304?pt=128027998&ct=website_traffic&mt=8"

MONTHS_DE = ["Januar", "Februar", "M\u00e4rz", "April", "Mai", "Juni",
             "Juli", "August", "September", "Oktober", "November", "Dezember"]

PHASE_LABEL_DE = {
    "new": "Neumond", "full": "Vollmond",
    "first-quarter": "Erstes Viertel", "last-quarter": "Letztes Viertel",
}


def to_cet(utc_str):
    dt_naive = datetime.fromisoformat(utc_str)
    dt_utc = dt_naive.replace(tzinfo=timezone.utc)
    year = dt_utc.year
    mar_last = datetime(year, 3, 31)
    while mar_last.weekday() != 6:
        mar_last -= timedelta(days=1)
    oct_last = datetime(year, 10, 31)
    while oct_last.weekday() != 6:
        oct_last -= timedelta(days=1)
    is_summer = (mar_last.replace(hour=1, tzinfo=timezone.utc)
                 <= dt_utc < oct_last.replace(hour=1, tzinfo=timezone.utc))
    offset = 2 if is_summer else 1
    local = dt_naive + timedelta(hours=offset)
    return f"{local.strftime('%H:%M')} {'CEST' if is_summer else 'CET'}"


# 12 monthly recommendations for haircuts by lunar phase
# Each entry: month_idx, focus (which phase best for which haircut in this month)
MONTHLY_FOCUS = [
    {"focus": "Januar - pflegende Schnitte", "advice": "Im Januar eignet sich der abnehmende Mond (um den 10.01.) hervorragend fur pflegende Spliss-Schnitte - das Haar bleibt lang gesund. Wer Volumen will, schneidet um den 26.01. (zunehmender Mond)."},
    {"focus": "Februar - Frische nach dem Winter", "advice": "Der Februar-Vollmond am 01.02. ist ideal fur kraftvolle Veranderungen - ein neuer Schnitt wachst in den Fruhlingsmonaten schnell nach. Neumond-Phase (17.02.) fur Form-halten."},
    {"focus": "Marz - Vorbereitung Fruhjahr", "advice": "Mitte Marz (um den Neumond am 19.03.) ist die perfekte Zeit fur einen pflegenden Schnitt vor der warmen Jahreszeit. Erstes Viertel (25.03.) fur Volumen und kraftige Schnitte."},
    {"focus": "April - Wachsen lassen", "advice": "Wer im April langere Haare will, schneidet um den Vollmond (02.04.). Fur Spliss-Schnitt ohne Nachwuchs-Effekt ist das letzte Viertel (10.04.) die richtige Wahl."},
    {"focus": "Mai - Form bewahren", "advice": "Der Mai hat 2026 zwei Vollmonde (01.05. und 31.05.). Beide sind Schnitt-Tage fur kraftige Veranderungen. Fur Pony-Schnitt oder Form-Korrektur besser Neumond am 16.05."},
    {"focus": "Juni - Sommer-Schnitt", "advice": "Vollmond am 29.06. ist klassischer Schnitt-Tag - ideal vor dem Sommer. Aber: Kraftige Vollmond-Schnitte wachsen in der Hitze schnell nach, also nur wenn man es so will."},
    {"focus": "Juli - Pflege-Schnitt", "advice": "Sommerhitze strapaziert das Haar. Ein pflegender Schnitt im letzten Viertel (07.07.) entfernt Spliss ohne Nachwuchs-Druck. Coloration im Neumond (14.07.) halt langer."},
    {"focus": "August - Vorbereitung Herbst", "advice": "Wer im Herbst mit kurzen Haaren starten will, schneidet um den Vollmond (28.08.). Der abnehmende Mond (06.08.) eignet sich fur Colorationen - sie verblassen langsamer."},
    {"focus": "September - Frischer Look", "advice": "September ist der klassische Monat fur eine typgerechte Veranderung. Vollmond am 26.09. ist Schnitt-Tag, Neumond am 11.09. fur Form-Korrekturen."},
    {"focus": "Oktober - Winterfest", "advice": "Ein pflegender Schnitt im Oktober bereitet das Haar auf den Winter vor. Vollmond am 26.10. fur Form-halten, letztes Viertel (03.10.) fur klassischen Herrenschnitt."},
    {"focus": "November - Schonende Pflege", "advice": "Im November sind die Haare oft strapaziert. Sanfter Spliss-Schnitt im abnehmenden Mond (01.11.). Vollmond (24.11.) fur Colorationen - sie wirken intensiver."},
    {"focus": "Dezember - Festtage", "advice": "Wer zu Weihnachten mit perfektem Look glanzen will, schneidet um den Vollmond am 24.12. - das Haar hat dann Zeit, sich zu setzen. Letztes Viertel (30.12.) fur intensive Colorationen."},
]


def build():
    events = sorted(json.load(open(DATA_FILE)), key=lambda x: x["utc"])
    by_month = {}
    for ev in events:
        ym = ev["utc"][:7]
        by_month.setdefault(ym, []).append(ev)

    # build 12 month tables
    month_blocks = []
    for i in range(12):
        ym = f"2026-{i + 1:02d}"
        month_name = f"{MONTHS_DE[i]} 2026"
        month_events = sorted(by_month.get(ym, []), key=lambda x: x["utc"])
        focus = MONTHLY_FOCUS[i]
        # build small table with phase times for this month
        rows = []
        for ev in month_events:
            utc_dt = datetime.fromisoformat(ev["utc"])
            date_str = utc_dt.strftime("%d.%m.%Y")
            label = PHASE_LABEL_DE[ev["phase"]]
            # recommendation per phase
            rec_map = {
                "new": "Form-halten",
                "full": "Kraftig wachsen",
                "first-quarter": "Volumen",
                "last-quarter": "Spliss-Schnitt",
            }
            rec = rec_map.get(ev["phase"], "")
            rows.append(
                f'<tr class="border-b border-white/5 last:border-0">'
                f'<td class="py-2 pr-4 font-medium text-slate-200 whitespace-nowrap">{label}</td>'
                f'<td class="py-2 pr-4 text-slate-300 whitespace-nowrap">{date_str}</td>'
                f'<td class="py-2 pr-4 text-slate-400 whitespace-nowrap">{utc_dt.strftime("%H:%M")} UTC / {to_cet(ev["utc"])}</td>'
                f'<td class="py-2 text-slate-300">{rec}</td>'
                f'</tr>'
            )
        block = (
            f'<div class="rounded-2xl border border-white/10 bg-night-900/70 p-6">'
            f'<h3 class="text-lg font-semibold text-white">{month_name}</h3>'
            f'<p class="mt-2 text-sm text-slate-300"><strong class="text-moon-300">{focus["focus"]}:</strong> {focus["advice"]}</p>'
            f'<div class="mt-4 overflow-x-auto">'
            f'<table class="w-full min-w-[600px] text-sm">'
            f'<thead><tr class="border-b border-white/10 text-left text-slate-500">'
            f'<th class="pb-2 pr-4 font-medium">Phase</th>'
            f'<th class="pb-2 pr-4 font-medium">Datum</th>'
            f'<th class="pb-2 pr-4 font-medium">Zeit (UTC / MEZ)</th>'
            f'<th class="pb-2 font-medium">Schnitt-Tipp</th>'
            f'</tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div></div>'
        )
        month_blocks.append(block)
    month_tables_html = "\n".join(month_blocks)

    # build JSON-LD
    event_items = []
    for ev in events:
        utc_dt = datetime.fromisoformat(ev["utc"])
        event_items.append({
            "@type": "Event",
            "name": f"{PHASE_LABEL_DE[ev['phase']]} - {MONTHS_DE[int(ev['utc'][5:7]) - 1]} 2026",
            "startDate": ev["utc"],
        })
    faq = [
        {"q": "Wann ist der beste Tag fur einen Haarschnitt 2026?",
         "a": "Das hangt vom gewunschten Ergebnis ab: Im zunehmenden Mond (zwischen Neumond und Vollmond) wachsen Haare schneller - ideal fur kraftige Schnitte. Im abnehmenden Mond (zwischen Vollmond und Neumond) bleibt die Form langer erhalten - ideal fur Form-halten und Pflegeschnitte."},
        {"q": "Wann sollte ich meine Haare nicht schneiden?",
         "a": "Viele Friseure und Anhanger der Tradition empfehlen, an Vollmond-Tagen aufwendige Colorationen zu vermeiden, da das Haar dann empfindlicher reagieren kann. Fur einfache Schnitte ist der Vollmond jedoch ideal."},
        {"q": "Funktioniert der Mondkalender fur Haare wirklich?",
         "a": "Es gibt keine eindeutige wissenschaftliche Evidenz fur den Einfluss des Mondes auf das Haarwachstum. Die Empfehlungen basieren auf jahrhundertealter Tradition. Probieren Sie es selbst aus und beobachten Sie, ob Sie einen Unterschied bemerken."},
        {"q": "Welche Mondphase eignet sich fur Colorationen?",
         "a": "Im abnehmenden Mond (nach Vollmond) verblassen Colorationen langsamer, weil das Haar langsamer nachwachst. Der Neumond gilt als ideale Phase fur intensive Farbbehandlungen."},
        {"q": "Wann sollte ich einen Pony schneiden?",
         "a": "Fur einen Pony, der langsamer nachwachsen soll, schneiden Sie im abnehmenden Mond (letztes Viertel). Wer einen Pony will, der schnell die gewunschte Lange erreicht, schneidet im zunehmenden Mond (erstes Viertel)."},
    ]
    article_ld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "Haarschnitt nach dem Mond 2026 - Die besten Schnitt-Termine",
        "description": "Haarschnitt nach dem Mond 2026: Welche Mondphase eignet sich fur welchen Schnitt? Monatliche Empfehlungen fur kraftige Schnitte, Spliss-Pflege und Colorationen.",
        "url": "https://mondplan.100ideas.net/de/haarschnitt-nach-dem-mond-2026.html",
        "inLanguage": "de",
        "datePublished": "2026-08-21",
        "dateModified": "2026-08-21",
        "author": {"@type": "Organization", "name": "100ideas"},
        "publisher": {
            "@type": "Organization",
            "name": "100ideas",
            "logo": {"@type": "ImageObject", "url": "https://mondplan.100ideas.net/assets/favicon.svg"},
        },
    }
    breadcrumb_ld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Startseite", "item": "https://mondplan.100ideas.net/de/"},
            {"@type": "ListItem", "position": 2, "name": "Haarschnitt nach dem Mond 2026",
             "item": "https://mondplan.100ideas.net/de/haarschnitt-nach-dem-mond-2026.html"},
        ],
    }
    faq_ld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}}
            for f in faq
        ],
    }
    events_ld = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "2026 Mondphasen - Schnitt-Tipps",
        "numberOfItems": len(event_items),
        "itemListElement": event_items,
    }
    app_ld = {
        "@context": "https://schema.org",
        "@type": "MobileApplication",
        "name": "MondPlan - Biodynamischer Mondkalender",
        "operatingSystem": "iOS 16.0 oder hoher",
        "applicationCategory": "LifestyleApplication",
        "offers": {"@type": "Offer", "price": "0.00", "priceCurrency": "EUR"},
        "url": "https://mondplan.100ideas.net/de/haarschnitt-nach-dem-mond-2026.html",
        "sameAs": ["https://apps.apple.com/app/id6758746304"],
    }
    faq_accordion = []
    for f in faq:
        faq_accordion.append(
            f'<details class="group rounded-2xl border border-white/10 bg-night-900/70 p-5">'
            f'<summary class="flex cursor-pointer items-center justify-between gap-4 text-base font-medium text-white">'
            f'<span>{f["q"]}</span>'
            f'<svg class="h-5 w-5 flex-shrink-0 text-moon-400 transition group-open:rotate-180" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>'
            f'</summary>'
            f'<p class="mt-3 text-sm leading-relaxed text-slate-300">{f["a"]}</p>'
            f'</details>'
        )
    faq_accordion_html = "".join(faq_accordion)

    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <title>Haarschnitt nach dem Mond 2026 - Die besten Schnitt-Termine</title>
  <meta name="description" content="Haarschnitt nach dem Mond 2026: Welche Mondphase eignet sich fur welchen Schnitt? Monatliche Empfehlungen fur kraftige Schnitte, Spliss-Pflege und Colorationen.">
  <meta name="apple-itunes-app" content="app-id=6758746304">
  <link rel="canonical" href="https://mondplan.100ideas.net/de/haarschnitt-nach-dem-mond-2026.html">
  <meta name="theme-color" content="#0a0f24">
  <meta name="author" content="100ideas">

  <link rel="alternate" hreflang="de" href="https://mondplan.100ideas.net/de/haarschnitt-nach-dem-mond-2026.html">
  <link rel="alternate" hreflang="x-default" href="https://mondplan.100ideas.net/de/haarschnitt-nach-dem-mond-2026.html">

  <meta property="og:type" content="article">
  <meta property="og:site_name" content="MondPlan">
  <meta property="og:title" content="Haarschnitt nach dem Mond 2026 - Die besten Schnitt-Termine">
  <meta property="og:description" content="12 Monate, 48 Schnitt-Empfehlungen. Welche Mondphase eignet sich fur welchen Haarschnitt?">
  <meta property="og:url" content="https://mondplan.100ideas.net/de/haarschnitt-nach-dem-mond-2026.html">
  <meta property="og:image" content="https://mondplan.100ideas.net/assets/og-image-de.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:locale" content="de_DE">

  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="Haarschnitt nach dem Mond 2026">
  <meta name="twitter:description" content="12 Monate Schnitt-Empfehlungen nach dem Mond.">
  <meta name="twitter:image" content="https://mondplan.100ideas.net/assets/og-image-de.png">

  <link rel="icon" type="image/svg+xml" href="../assets/favicon.svg?v=2">
  <link rel="apple-touch-icon" href="../assets/apple-touch-icon.png?v=2">
  <link rel="stylesheet" href="../assets/tailwind.css?v=2">

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
    <nav class="mx-auto flex max-w-6xl items-center justify-between px-5 py-4" aria-label="Hauptnavigation">
      <a href="index.html" class="flex items-center gap-2 text-base font-semibold text-white">
        <span aria-hidden="true">&#9790;</span>
        MondPlan
      </a>
      <div class="hidden items-center gap-7 text-sm text-slate-300 md:flex">
        <a href="mondphasen-2026.html" class="transition hover:text-moon-300">Mondphasen 2026</a>
        <a href="vollmond-2026.html" class="transition hover:text-moon-300">Vollmond 2026</a>
        <a href="mondkalender-garten-2026.html" class="transition hover:text-moon-300">Garten</a>
        <a href="#faq" class="transition hover:text-moon-300">FAQ</a>
      </div>
      <a href="{CAMPAIGN_LINK}" class="rounded-full bg-moon-300 px-4 py-2 text-sm font-semibold text-night-950 transition hover:bg-moon-200">App laden</a>
    </nav>
  </header>

  <main>
    <section class="starfield relative overflow-hidden" aria-labelledby="page-title">
      <div class="pointer-events-none absolute inset-0 bg-gradient-to-b from-night-900/40 via-transparent to-night-950" aria-hidden="true"></div>
      <div class="mx-auto max-w-6xl px-5 py-16 md:py-20">
        <p class="text-sm font-semibold uppercase tracking-widest text-moon-400">Schonheit &amp; Mond - 2026</p>
        <h1 id="page-title" class="mt-3 text-3xl font-bold tracking-tight text-white md:text-4xl lg:text-5xl">
          Haarschnitt nach dem Mond 2026
        </h1>
        <p class="mt-5 max-w-2xl text-lg leading-relaxed text-slate-300">
          Welche Mondphase eignet sich fur welchen Haarschnitt? Zwolf Monate Empfehlungen
          fur kraftige Schnitte, Spliss-Pflege und Colorationen - nach der Tradition
          der Bauernkalender und moderner Friseurkunst.
        </p>
        <div class="mt-6 flex flex-wrap gap-x-6 gap-y-2 text-sm text-slate-400">
          <span class="flex items-center gap-1.5">
            <svg class="h-4 w-4 text-moon-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>
            12 Monate, 48 Schnitt-Tipps
          </span>
          <span class="flex items-center gap-1.5">
            <svg class="h-4 w-4 text-moon-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>
            Daten exakt nach Jean Meeus
          </span>
        </div>
      </div>
    </section>

    <section class="border-y border-white/5 bg-night-900/60" aria-labelledby="phases-title">
      <div class="mx-auto max-w-6xl px-5 py-14">
        <h2 id="phases-title" class="text-2xl font-bold tracking-tight text-white">Die vier Phasen und ihre Bedeutung fur das Haar</h2>
        <ol class="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <li class="rounded-2xl border border-white/10 bg-night-950/60 p-5">
            <h3 class="font-semibold text-white">Neumond</h3>
            <p class="mt-1 text-sm text-slate-400">Form-halten: Haare wachsen langsamer nach. Ideale Zeit fur pflegende Schnitte, Form-Korrekturen, Pony-Schnitt.</p>
          </li>
          <li class="rounded-2xl border border-white/10 bg-night-950/60 p-5">
            <h3 class="font-semibold text-white">Zunehmender Mond</h3>
            <p class="mt-1 text-sm text-slate-400">Wachstumsphase: Haare wachsen schneller nach. Ideal fur kraftige Veranderungen, Bob-Schnitt, neue Looks.</p>
          </li>
          <li class="rounded-2xl border border-white/10 bg-night-950/60 p-5">
            <h3 class="font-semibold text-white">Vollmond</h3>
            <p class="mt-1 text-sm text-slate-400">Maximales Wachstum: Klassischer Schnitt-Tag fur kraftige Veranderungen. Intensive Colorationen moglich.</p>
          </li>
          <li class="rounded-2xl border border-white/10 bg-night-950/60 p-5">
            <h3 class="font-semibold text-white">Abnehmender Mond</h3>
            <p class="mt-1 text-sm text-slate-400">Beruhigungsphase: Spliss-Schnitte ohne Nachwuchs-Druck. Colorationen verblassen langsamer.</p>
          </li>
        </ol>
      </div>
    </section>

    <section class="mx-auto max-w-6xl px-5 py-14" aria-labelledby="months-title">
      <div class="max-w-2xl">
        <h2 id="months-title" class="text-2xl font-bold tracking-tight text-white">12 Monate Schnitt-Empfehlungen</h2>
        <p class="mt-3 text-slate-400">Fur jeden Monat: die vier Mondphasen mit Zeitangabe und passendem Schnitt-Tipp.</p>
      </div>

      <div class="mt-8 space-y-6">
        {month_tables_html}
      </div>
    </section>

    <section class="mx-auto max-w-3xl px-5 py-14" aria-labelledby="faq-title" id="faq">
      <h2 id="faq-title" class="text-2xl font-bold tracking-tight text-white">Haufige Fragen</h2>
      <div class="mt-8 space-y-3">
        {faq_accordion_html}
      </div>
    </section>

    <section class="border-t border-white/5 bg-night-900/60">
      <div class="mx-auto max-w-6xl px-5 py-14">
        <h2 class="text-2xl font-bold tracking-tight text-white">Weitere Mondkalender</h2>
        <ul class="mt-6 grid gap-4 sm:grid-cols-2">
          <li><a href="mondphasen-2026.html" class="block rounded-2xl border border-white/10 bg-night-950/60 p-5 transition hover:border-moon-400/30">
            <p class="text-sm font-semibold text-white">Mondphasen 2026</p>
            <p class="mt-1 text-xs text-slate-400">Vollstandiger Mondkalender mit allen 4 Phasen pro Monat.</p>
          </a></li>
          <li><a href="vollmond-2026.html" class="block rounded-2xl border border-white/10 bg-night-950/60 p-5 transition hover:border-moon-400/30">
            <p class="text-sm font-semibold text-white">Vollmond 2026</p>
            <p class="mt-1 text-xs text-slate-400">Alle 13 Vollmonde, Namen, Daten.</p>
          </a></li>
          <li><a href="neumond-2026.html" class="block rounded-2xl border border-white/10 bg-night-950/60 p-5 transition hover:border-moon-400/30">
            <p class="text-sm font-semibold text-white">Neumond 2026</p>
            <p class="mt-1 text-xs text-slate-400">Alle 12 Neumonde, Daten, Bedeutung.</p>
          </a></li>
          <li><a href="mondkalender-garten-2026.html" class="block rounded-2xl border border-white/10 bg-night-950/60 p-5 transition hover:border-moon-400/30">
            <p class="text-sm font-semibold text-white">Mondkalender Garten 2026</p>
            <p class="mt-1 text-xs text-slate-400">Aussaat, Ernte und Pflege nach Mond.</p>
          </a></li>
        </ul>
      </div>
    </section>

    <section class="mx-auto max-w-4xl px-5 py-20 text-center">
      <h2 class="text-3xl font-bold tracking-tight text-white">MondPlan App laden</h2>
      <p class="mt-3 text-slate-300">Alle Schnitt-Tipps direkt auf dem iPhone - mit Erinnerungen und Mondphase heute.</p>
      <a href="{CAMPAIGN_LINK}" class="mt-8 inline-block rounded-full bg-moon-300 px-8 py-3 text-base font-semibold text-night-950 transition hover:bg-moon-200">MondPlan App laden</a>
    </section>
  </main>

  <footer class="border-t border-white/5 bg-night-900/60">
    <div class="mx-auto max-w-6xl px-5 py-10 flex flex-col items-start justify-between gap-6 sm:flex-row sm:items-center">
      <p class="text-sm text-slate-500">&copy; 2026 100ideas. Daten nach Jean Meeus &copy; 1998.</p>
      <nav class="flex flex-col gap-3 text-sm text-slate-400 sm:flex-row sm:items-center sm:gap-8" aria-label="Fussnavigation">
        <a href="index.html" class="transition hover:text-moon-300">Startseite</a>
        <a href="privacy.html" class="transition hover:text-moon-300">Datenschutz</a>
        <a href="support.html" class="transition hover:text-moon-300">Support</a>
        <a href="mondphasen-2026.html" class="transition hover:text-moon-300">Mondphasen 2026</a>
        <a href="{CAMPAIGN_LINK}" class="transition hover:text-moon-300">App Store</a>
      </nav>
    </div>
  </footer>
</body>
</html>
"""
    out = os.path.join(BASE, "de", "haarschnitt-nach-dem-mond-2026.html")
    open(out, "w", encoding="utf-8").write(html)
    print(f"  wrote {os.path.relpath(out, BASE)} ({os.path.getsize(out)} bytes) - {len(event_items)} events, {len(faq)} faq")


if __name__ == "__main__":
    build()
