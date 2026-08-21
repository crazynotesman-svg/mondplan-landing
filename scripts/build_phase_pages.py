"""Build /moon-phases-2026.html (EN) and /de/mondphasen-2026.html (DE) from
data/moon-phases-2026.json + the templates in scripts/templates/.

Injects:
  {{TABLE_EN}} / {{TABLE_DE}}   - monthly phase tables
  {{EVENTS_EN}} / {{EVENTS_DE}} - ItemList of Event JSON-LD

Usage: python scripts/build_phase_pages.py
"""
import json
import os
import re
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "moon-phases-2026.json")
TPL_EN = os.path.join(ROOT, "scripts", "templates", "moon-phases-2026.template.html")
TPL_DE = os.path.join(ROOT, "scripts", "templates", "mondphasen-2026.template.html")
OUT_EN = os.path.join(ROOT, "moon-phases-2026.html")
OUT_DE = os.path.join(ROOT, "de", "mondphasen-2026.html")

MONTHS_EN = ["January", "February", "March", "April", "May", "June",
             "July", "August", "September", "October", "November", "December"]
MONTHS_DE = ["Januar", "Februar", "März", "April", "Mai", "Juni",
             "Juli", "August", "September", "Oktober", "November", "Dezember"]

PHASE_EN = {"new": "New Moon", "first-quarter": "First Quarter",
            "full": "Full Moon", "last-quarter": "Last Quarter"}
PHASE_DE = {"new": "Neumond", "first-quarter": "Erstes Viertel",
            "full": "Vollmond", "last-quarter": "Letztes Viertel"}


def load():
    with open(DATA, encoding="utf-8") as f:
        return json.load(f)


def by_month(phases):
    groups = defaultdict(list)
    for p in phases:
        groups[p["utc"][5:7]].append(p)
    for k in groups:
        groups[k].sort(key=lambda r: r["utc"])
    return groups


def fmt_date_en(iso):
    y, m, d = iso[:10].split("-")
    return f"{MONTHS_EN[int(m)-1]} {int(d)}"


def fmt_date_de(iso):
    y, m, d = iso[:10].split("-")
    return f"{int(d)}. {MONTHS_DE[int(m)-1]}"


def build_table(phases, lang):
    groups = by_month(phases)
    months = MONTHS_EN if lang == "en" else MONTHS_DE
    phase_names = PHASE_EN if lang == "en" else PHASE_DE
    tz_label = "CET/CEST" if lang == "en" else "MEZ/MESZ"
    blocks = []
    for mm in sorted(groups):
        rows = groups[mm]
        month_name = months[int(mm) - 1]
        trs = []
        for r in rows:
            date_iso, time_utc = r["utc"].split(" ")
            cet_date, cet_time = r["cet"].split(" ")
            tz = "CEST" if r["cest"] == 2 else "CET"
            tz_de = "MESZ" if r["cest"] == 2 else "MEZ"
            tz_show = tz if lang == "en" else tz_de
            date_show = fmt_date_en(date_iso) if lang == "en" else fmt_date_de(date_iso)
            trs.append(
                f'          <tr class="border-b border-white/5 last:border-0">'
                f'<td class="py-2.5 pr-4 font-medium text-slate-200">{phase_names[r["phase"]]}</td>'
                f'<td class="py-2.5 pr-4 whitespace-nowrap text-slate-300">{date_show}</td>'
                f'<td class="py-2.5 pr-4 text-slate-400">{time_utc} UTC</td>'
                f'<td class="py-2.5 text-slate-300 whitespace-nowrap">{cet_time} {tz_show}</td></tr>'
            )
        blocks.append(
            '<div class="rounded-2xl border border-white/10 bg-night-900/70 p-6">'
            f'<h3 class="text-lg font-semibold text-white">{month_name} 2026</h3>'
            '<div class="mt-4 overflow-x-auto">'
            '<table class="w-full min-w-[520px] text-sm">'
            '<thead><tr class="border-b border-white/10 text-left text-slate-500">'
            f'<th class="pb-2 pr-4 font-medium">Phase</th><th class="pb-2 pr-4 font-medium">Date</th>'
            f'<th class="pb-2 pr-4 font-medium">UTC</th><th class="pb-2 font-medium">{tz_label}</th></tr></thead>'
            '<tbody>' + "\n".join(trs) + "\n" + '          </tbody></table></div></div>'
        )
    return "\n\n".join(blocks)


def build_events(phases, lang):
    phase_names = PHASE_EN if lang == "en" else PHASE_DE
    items = []
    for i, r in enumerate(phases, 1):
        date_iso, time_utc = r["utc"].split(" ")
        start = f"{date_iso}T{time_utc}:00Z"
        name = f'{phase_names[r["phase"]]} – {fmt_date_en(date_iso)} 2026' if lang == "en" \
            else f'{phase_names[r["phase"]]} – {fmt_date_de(date_iso)} 2026'
        items.append(
            '      { "@type": "ListItem", "position": %d, "item": {'
            '"@type": "Event", "name": %s, "startDate": "%s", '
            '"eventAttendanceMode": "https://schema.org/OnlineEventAttendanceMode", '
            '"location": { "@type": "Place", "name": "Worldwide (UTC)" } } }'
            % (i, json.dumps(name, ensure_ascii=False), start)
        )
    return ('{\n'
            '  "@context": "https://schema.org",\n'
            '  "@type": "ItemList",\n'
            '  "name": "Moon Phases 2026",\n'
            '  "itemListElement": [\n'
            + ",\n".join(items) +
            '\n  ]\n}'
            )


def main():
    phases = load()
    table_en = build_table(phases, "en")
    table_de = build_table(phases, "de")
    events_en = build_events(phases, "en")
    events_de = build_events(phases, "de")

    for tpl, out, repl in [
        (TPL_EN, OUT_EN, {"{{TABLE_EN}}": table_en, "{{EVENTS_EN}}": events_en}),
        (TPL_DE, OUT_DE, {"{{TABLE_DE}}": table_de, "{{EVENTS_DE}}": events_de}),
    ]:
        with open(tpl, encoding="utf-8") as f:
            html = f.read()
        for k, v in repl.items():
            html = html.replace(k, v)
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
