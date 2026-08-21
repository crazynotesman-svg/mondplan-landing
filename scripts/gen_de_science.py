"""Generate the German version of how-moon-phases-work.html from the
English file by applying a curated EN->DE translation map. This keeps the
two pages structurally identical (JSON-LD, SVG diagram, links) while
localizing all visible copy and the German-specific metadata.

Usage: python scripts/gen_de_science.py
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EN = os.path.join(BASE, "en", "how-moon-phases-work.html")
DE = os.path.join(BASE, "de", "mondphasen-erklaert.html")

# (exact english substring, german replacement) - applied in order
TRANSLATIONS = [
    # ---- head ----
    ("<html lang=\"en\">", "<html lang=\"de\">"),
    ("<title>How Moon Phases Work - The Science Behind the Lunar Cycle</title>",
     "<title>Mondphasen erkl\u00e4rt - die Wissenschaft hinter dem Mondzyklus</title>"),
    ("<meta name=\"description\" content=\"Why does the moon have phases? The science of the lunar cycle explained: orbital geometry, the 8 phases, the terminator and the 29.53-day synodic month.\">",
     "<meta name=\"description\" content=\"Warum hat der Mond Phasen? Die Wissenschaft hinter dem Mondzyklus: Orbitalgeometrie, die 8 Mondphasen, der Terminator und der synodische Monat von 29,53 Tagen.\">"),
    ("<link rel=\"canonical\" href=\"https://mondplan.100ideas.net/en/how-moon-phases-work.html\">",
     "<link rel=\"canonical\" href=\"https://mondplan.100ideas.net/de/mondphasen-erklaert.html\">"),
    ("<link rel=\"alternate\" hreflang=\"en\" href=\"https://mondplan.100ideas.net/en/how-moon-phases-work.html\">",
     "<link rel=\"alternate\" hreflang=\"de\" href=\"https://mondplan.100ideas.net/de/mondphasen-erklaert.html\">"),
    ("<link rel=\"alternate\" hreflang=\"de\" href=\"https://mondplan.100ideas.net/de/mondphasen-erklaert.html\">",
     "<link rel=\"alternate\" hreflang=\"en\" href=\"https://mondplan.100ideas.net/en/how-moon-phases-work.html\">"),
    ("<link rel=\"alternate\" hreflang=\"x-default\" href=\"https://mondplan.100ideas.net/en/how-moon-phases-work.html\">",
     "<link rel=\"alternate\" hreflang=\"x-default\" href=\"https://mondplan.100ideas.net/de/mondphasen-erklaert.html\">"),
    # og
    ("<meta property=\"og:title\" content=\"How Moon Phases Work - The Science Behind the Lunar Cycle\">",
     "<meta property=\"og:title\" content=\"Mondphasen erkl\u00e4rt - die Wissenschaft hinter dem Mondzyklus\">"),
    ("<meta property=\"og:description\" content=\"Orbital geometry, the 8 phases, the terminator and the 29.53-day synodic month - explained.\">",
     "<meta property=\"og:description\" content=\"Orbitalgeometrie, die 8 Mondphasen, der Terminator und der synodische Monat von 29,53 Tagen - einfach erkl\u00e4rt.\">"),
    ("<meta property=\"og:url\" content=\"https://mondplan.100ideas.net/en/how-moon-phases-work.html\">",
     "<meta property=\"og:url\" content=\"https://mondplan.100ideas.net/de/mondphasen-erklaert.html\">"),
    ("<meta property=\"og:image\" content=\"https://mondplan.100ideas.net/assets/og-image.png?v=3\">",
     "<meta property=\"og:image\" content=\"https://mondplan.100ideas.net/assets/og-image-de.png?v=3\">"),
    ("<meta property=\"og:locale\" content=\"en_US\">",
     "<meta property=\"og:locale\" content=\"de_DE\">"),
    ("<meta property=\"og:locale:alternate\" content=\"de_DE\">",
     "<meta property=\"og:locale:alternate\" content=\"en_US\">"),
    # twitter
    ("<meta name=\"twitter:title\" content=\"How Moon Phases Work\">",
     "<meta name=\"twitter:title\" content=\"Mondphasen erkl\u00e4rt\">"),
    ("<meta name=\"twitter:description\" content=\"The science of the lunar cycle explained.\">",
     "<meta name=\"twitter:description\" content=\"Die Wissenschaft hinter dem Mondzyklus - einfach erkl\u00e4rt.\">"),
    ("<meta name=\"twitter:image\" content=\"https://mondplan.100ideas.net/assets/og-image.png?v=3\">",
     "<meta name=\"twitter:image\" content=\"https://mondplan.100ideas.net/assets/og-image-de.png?v=3\">"),
    # JSON-LD Article
    ('"headline": "How Moon Phases Work - The Science Behind the Lunar Cycle"',
     '"headline": "Mondphasen erkl\u00e4rt - die Wissenschaft hinter dem Mondzyklus"'),
    ('"description": "Why does the moon have phases? The science of the lunar cycle explained: orbital geometry, the 8 phases, the terminator and the 29.53-day synodic month."',
     '"description": "Warum hat der Mond Phasen? Die Wissenschaft hinter dem Mondzyklus: Orbitalgeometrie, die 8 Mondphasen, der Terminator und der synodische Monat von 29,53 Tagen."'),
    ('"url": "https://mondplan.100ideas.net/en/how-moon-phases-work.html"',
     '"url": "https://mondplan.100ideas.net/de/mondphasen-erklaert.html"'),
    ('"inLanguage": "en"', '"inLanguage": "de"'),
    # JSON-LD Breadcrumb
    ('{"@type": "ListItem", "position": 2, "name": "How Moon Phases Work", "item": "https://mondplan.100ideas.net/en/how-moon-phases-work.html"}',
     '{"@type": "ListItem", "position": 2, "name": "Mondphasen erkl\u00e4rt", "item": "https://mondplan.100ideas.net/de/mondphasen-erklaert.html"}'),
    # JSON-LD FAQ questions (5)
    ('{"@type": "Question", "name": "Why does the moon have phases?", "acceptedAnswer": {"@type": "Answer", "text": "The moon does not produce its own light - it reflects sunlight. As the moon orbits Earth, we see different fractions of its sunlit half, producing the phases. Half of the moon is always lit; the phase depends on how much of that lit half faces Earth."}}',
     '{"@type": "Question", "name": "Warum hat der Mond Phasen?", "acceptedAnswer": {"@type": "Answer", "text": "Der Mond hat kein eigenes Licht - er reflektiert das Sonnenlicht. W\u00e4hrend der Mond die Erde umkreist, sehen wir verschiedene Anteile seiner beleuchteten H\u00e4lfte. Eine H\u00e4lfte des Mondes ist immer beleuchtet; die Phase h\u00e4ngt davon ab, wie viel davon der Erde zugewandt ist."}}'),
    ('{"@type": "Question", "name": "How long is one full lunar cycle?", "acceptedAnswer": {"@type": "Answer", "text": "The synodic month - the time between two identical phases (e.g. full moon to full moon) - averages 29.53059 days (about 29 days, 12 hours, 44 minutes)."}}',
     '{"@type": "Question", "name": "Wie lange dauert ein kompletter Mondzyklus?", "acceptedAnswer": {"@type": "Answer", "text": "Der synodische Monat - die Zeit zwischen zwei gleichen Phasen (z. B. Vollmond zu Vollmond) - dauert durchschnittlich 29,53059 Tage (etwa 29 Tage, 12 Stunden, 44 Minuten)."}}'),
    ('{"@type": "Question", "name": "Why is a month 30 or 31 days but the lunar cycle 29.5?", "acceptedAnswer": {"@type": "Answer", "text": "The Gregorian calendar is solar-based (365.2425 days per year). A lunar year of 12 synodic months is about 354.4 days - roughly 11 days shorter - which is why lunar calendars (e.g. the Islamic calendar) drift against the seasons unless intercalary months are added."}}',
     '{"@type": "Question", "name": "Warum hat ein Monat 30 oder 31 Tage, der Mondzyklus aber nur 29,5?", "acceptedAnswer": {"@type": "Answer", "text": "Der Gregorianische Kalender ist sonnenbasiert (365,2425 Tage pro Jahr). Ein Mondjahr aus 12 synodischen Monaten ist etwa 354,4 Tage lang - rund 11 Tage k\u00fcrzer. Deshalb verschieben sich Mondkalender (z. B. der islamische Kalender) gegen die Jahreszeiten, sofern keine Schaltmonate eingef\u00fcgt werden."}}'),
    ('{"@type": "Question", "name": "What is the terminator?", "acceptedAnswer": {"@type": "Answer", "text": "The terminator is the boundary between the illuminated and dark parts of the moon\'s disc. Its curve (an ellipse as seen from Earth) gives each phase its distinctive shape - a thin ellipse for crescents, a straight line at the quarters, and a fat ellipse for gibbous phases."}}',
     '{"@type": "Question", "name": "Was ist der Terminator?", "acceptedAnswer": {"@type": "Answer", "text": "Der Terminator ist die Grenze zwischen dem beleuchteten und dem dunklen Teil der Mondscheibe. Seine Kurve (von der Erde aus gesehen eine Ellipse) gibt jeder Phase ihre charakteristische Form - eine d\u00fcnne Ellipse f\u00fcr Sicheln, eine gerade Linie bei den Vierteln und eine fette Ellipse f\u00fcr die zunehmenden und abnehmenden Monde."}}'),
    ('{"@type": "Question", "name": "Does the moon actually change shape?", "acceptedAnswer": {"@type": "Answer", "text": "No. The moon is always a sphere, and half of it is always sunlit. The apparent change in shape is only a change in the fraction of the sunlit half that faces Earth."}}',
     '{"@type": "Question", "name": "Ver\u00e4ndert der Mond wirklich seine Form?", "acceptedAnswer": {"@type": "Answer", "text": "Nein. Der Mond ist immer eine Kugel, und eine H\u00e4lfte ist immer von der Sonne beleuchtet. Die scheinbare Form\u00e4nderung ist nur eine \u00c4nderung des Anteils der beleuchteten H\u00e4lfte, der der Erde zugewandt ist."}}'),
    # JSON-LD MobileApplication
    ('"url": "https://mondplan.100ideas.net/en/how-moon-phases-work.html"',
     '"url": "https://mondplan.100ideas.net/de/mondphasen-erklaert.html"'),
    ('"name": "MondPlan - Biodynamic Moon Calendar",',
     '"name": "MondPlan - Biodynamischer Mondkalender",'),
    # ---- body nav ----
    ("<a href=\"../index.html\" class=\"flex items-center gap-2 text-base font-semibold text-white\">",
     "<a href=\"index.html\" class=\"flex items-center gap-2 text-base font-semibold text-white\">"),
    ('<a href="../moon-phases-2026.html" class="transition hover:text-moon-300">Moon Phases 2026</a>',
     '<a href="mondphasen-2026.html" class="transition hover:text-moon-300">Mondphasen 2026</a>'),
    ('<a href="full-moon-2026.html" class="transition hover:text-moon-300">Full Moon</a>',
     '<a href="vollmond-2026.html" class="transition hover:text-moon-300">Vollmond</a>'),
    ('<a href="new-moon-2026.html" class="transition hover:text-moon-300">New Moon</a>',
     '<a href="neumond-2026.html" class="transition hover:text-moon-300">Neumond</a>'),
    # related-links cards (block style) - hrefs must be localized too
    ('<li><a href="full-moon-2026.html" class="block rounded-2xl',
     '<li><a href="vollmond-2026.html" class="block rounded-2xl'),
    ('<li><a href="new-moon-2026.html" class="block rounded-2xl',
     '<li><a href="neumond-2026.html" class="block rounded-2xl'),
    ('<li><a href="blue-moon-2026.html" class="block rounded-2xl',
     '<li><a href="blauermond-2026.html" class="block rounded-2xl'),
    ('<a href="../de/mondphasen-erklaert.html" class="text-sm text-slate-400 transition hover:text-moon-300" rel="alternate" hreflang="de">DE</a>',
     '<a href="../en/how-moon-phases-work.html" class="text-sm text-slate-400 transition hover:text-moon-300" rel="alternate" hreflang="en">EN</a>'),
    ('>Get App</a>', '>App laden</a>'),
    # hero
    ("<p class=\"text-sm font-semibold uppercase tracking-widest text-moon-400\">Moon Science</p>",
     "<p class=\"text-sm font-semibold uppercase tracking-widest text-moon-400\">Mondwissenschaft</p>"),
    ("How Moon Phases Work", "Mondphasen erkl\u00e4rt"),
    ("The moon doesn't change shape - it just reflects sunlight from different\n          angles as it orbits Earth. Here is the geometry behind the phases you\n          see every night, in plain language.",
     "Der Mond ver\u00e4ndert nicht seine Form - er reflektiert nur Sonnenlicht aus\n          verschiedenen Winkeln, w\u00e4hrend er die Erde umkreist. Hier ist die Geometrie\n          hinter den Phasen, die Sie jede Nacht sehen, in einfacher Sprache."),
    ("Reviewed against Meeus &amp; NASA sources", "Gepr\u00fcft anhand von Meeus &amp; NASA-Quellen"),
    ("8 phases, 29.53 days", "8 Phasen, 29,53 Tage"),
    # section 1
    ("The single fact that explains everything", "Die eine Tatsache, die alles erkl\u00e4rt"),
    ("<strong class=\"text-white\">Half of the moon is always lit by the sun.</strong>",
     "<strong class=\"text-white\">Eine H\u00e4lfte des Mondes ist immer von der Sonne beleuchtet.</strong>"),
    ("The moon has no light of its own - it is a rocky sphere (about 3,474 km in diameter)\n            reflecting sunlight. Just like the Earth, exactly one half faces the sun at any moment,\n            and the other half is in darkness.",
     "Der Mond hat kein eigenes Licht - er ist eine felsige Kugel (etwa 3.474 km Durchmesser),\n            die das Sonnenlicht reflektiert. Genau wie bei der Erde ist zu jedem Zeitpunkt eine H\u00e4lfte\n            der Sonne zugewandt, die andere liegt im Dunkeln."),
    ("What changes is <em class=\"text-moon-300\">how much of that sunlit half we can see from Earth</em>.",
     "Was sich \u00e4ndert, ist <em class=\"text-moon-300\">wie viel von dieser beleuchteten H\u00e4lfte wir von der Erde aus sehen k\u00f6nnen</em>."),
    ("As the moon travels its orbit, the angle between the Sun, Earth and the Moon changes\n            continuously, so the portion of the lit half facing us grows, peaks, shrinks and resets\n            - that is the lunar cycle.",
     "W\u00e4hrend der Mond seine Bahn zieht, \u00e4ndert sich der Winkel zwischen Sonne, Erde und Mond\n            kontinuierlich. Der Anteil der beleuchteten H\u00e4lfte, der uns zugewandt ist, w\u00e4chst, erreicht\n            sein Maximum, schrumpft und setzt zur\u00fcck - das ist der Mondzyklus."),
    ("The moon orbits Earth in about <strong class=\"text-white\">27.3 days</strong> (sidereal month),\n            but because Earth itself moves around the Sun, the time between two identical phases is longer:\n            <strong class=\"text-white\">29.53 days</strong> (synodic month). That 29.53-day rhythm is what a\n            lunar calendar tracks.",
     "Der Mond umkreist die Erde in etwa <strong class=\"text-white\">27,3 Tagen</strong> (siderischer Monat),\n            aber weil sich die Erde selbst um die Sonne bewegt, ist die Zeit zwischen zwei gleichen Phasen l\u00e4nger:\n            <strong class=\"text-white\">29,53 Tage</strong> (synodischer Monat). Dieser 29,53-Tage-Rhythmus ist es,\n            den ein Mondkalender verfolgt."),
    ("The Sun-Moon-Earth geometry", "Die Sonne-Mond-Erde-Geometrie"),
    ("Diagram of the eight moon phases around the Earth, with the Sun off to the left",
     "Diagramm der acht Mondphasen um die Erde, mit der Sonne links"),
    ("Eight moon phases around Earth", "Acht Mondphasen um die Erde"),
    ("Sunlight comes from the left; the lit half of the moon always faces the Sun.",
     "Das Sonnenlicht kommt von links; die beleuchtete H\u00e4lfte des Mondes zeigt immer zur Sonne."),
    # section 2
    ("The eight phases, in order", "Die acht Phasen in Reihenfolge"),
    ("Each phase is a milestone in the 29.53-day cycle. The illuminated fraction follows a cosine curve: 0% at New Moon, 50% at the quarters, 100% at Full Moon.",
     "Jede Phase ist ein Meilenstein im 29,53-Tage-Zyklus. Der beleuchtete Anteil folgt einer Kosinuskurve: 0% bei Neumond, 50% bei den Vierteln, 100% bei Vollmond."),
    # 8 phase cards
    ("1. New Moon", "1. Neumond"),
    ("The moon is between Earth and the Sun; its lit half faces away. Invisible in the night sky. 0% illuminated.",
     "Der Mond steht zwischen Erde und Sonne; seine beleuchtete H\u00e4lfte zeigt von uns weg. Am Nachthimmel unsichtbar. 0% beleuchtet."),
    ("2. Waxing Crescent", "2. Zunehmende Sichel"),
    ("A thin sliver appears on the right (Northern Hemisphere). A few percent of the disc is lit.",
     "Eine d\u00fcnne Sichel erscheint rechts (Nordhalbkugel). Einige Prozent der Scheibe sind beleuchtet."),
    ("3. First Quarter", "3. Erstes Viertel"),
    ("Half the disc is lit (50%). The terminator is a straight line. Roughly 7.4 days after New Moon.",
     "Die halbe Scheibe ist beleuchtet (50%). Der Terminator ist eine gerade Linie. Etwa 7,4 Tage nach Neumond."),
    ("4. Waxing Gibbous", "4. Zunehmender Mond"),
    ("More than half lit, still growing (50-100%). The terminator curves outward to the right.",
     "Mehr als die H\u00e4lfte beleuchtet, weiter wachsend (50-100%). Der Terminator w\u00f6lbt sich nach rechts."),
    ("5. Full Moon", "5. Vollmond"),
    ("The whole sunlit half faces Earth (100%). The moon rises around sunset. ~14.8 days after New Moon.",
     "Die gesamte beleuchtete H\u00e4lfte zeigt zur Erde (100%). Der Mond geht etwa bei Sonnenuntergang auf. ~14,8 Tage nach Neumond."),
    ("6. Waning Gibbous", "6. Abnehmender Mond"),
    ("Still more than half lit, but decreasing. Light recedes from the right side first.",
     "Noch mehr als die H\u00e4lfte beleuchtet, aber abnehmend. Das Licht weicht zuerst von der rechten Seite."),
    ("7. Last Quarter", "7. Letztes Viertel"),
    ("Half lit again (50%), now on the left. ~22.1 days after New Moon.",
     "Wieder halb beleuchtet (50%), jetzt links. ~22,1 Tage nach Neumond."),
    ("8. Waning Crescent", "8. Abnehmende Sichel"),
    ("A thin sliver remains on the left, shrinking toward New Moon.",
     "Eine d\u00fcnne Sichel bleibt links, schrumpfend Richtung Neumond."),
    # section 3
    ("Why phases have their distinctive shapes", "Warum die Phasen ihre charakteristischen Formen haben"),
    ("The boundary between the lit and dark parts of the moon's face is called the\n            <strong class=\"text-white\">terminator</strong>. Seen from Earth it appears as the edge of an\n            ellipse - the projection of a circle (the terminator on the moon's sphere) onto our line of sight.",
     "Die Grenze zwischen dem beleuchteten und dem dunklen Teil der Mondoberfl\u00e4che hei\u00dft\n            <strong class=\"text-white\">Terminator</strong>. Von der Erde aus erscheint sie als Rand einer\n            Ellipse - die Projektion eines Kreises auf unsere Sichtlinie."),
    ("<strong class=\"text-moon-300\">Crescents:</strong> the terminator ellipse is thin, so only a narrow sliver is lit.",
     "<strong class=\"text-moon-300\">Sicheln:</strong> Die Terminator-Ellipse ist d\u00fcnn, daher ist nur eine schmale Sichel beleuchtet."),
    ("<strong class=\"text-moon-300\">Quarters:</strong> the ellipse degenerates into a straight line - exactly half lit.",
     "<strong class=\"text-moon-300\">Viertel:</strong> Die Ellipse entartet zu einer geraden Linie - genau halb beleuchtet."),
    ("<strong class=\"text-moon-300\">Gibbous phases:</strong> the ellipse is fat, so most of the disc is lit.",
     "<strong class=\"text-moon-300\">Zunehmende/abnehmende Monde:</strong> Die Ellipse ist fett, daher ist der gr\u00f6\u00dfte Teil der Scheibe beleuchtet."),
    ("<strong class=\"text-moon-300\">Full Moon:</strong> the terminator is not visible at all - the entire disc is sunlit.",
     "<strong class=\"text-moon-300\">Vollmond:</strong> Der Terminator ist gar nicht sichtbar - die gesamte Scheibe ist beleuchtet."),
    ("In the Northern Hemisphere the lit side grows from the <em>right</em> (waxing) and shrinks from the\n            <em>right</em> (waning). South of the equator this is mirrored. This page and the MondPlan app use the\n            Northern Hemisphere convention.",
     "Auf der Nordhalbkugel w\u00e4chst die beleuchtete Seite von <em>rechts</em> (zunehmend) und schrumpft von\n            <em>rechts</em> (abnehmend). S\u00fcdlich des \u00c4quators ist dies gespiegelt. Diese Seite und die MondPlan-App\n            verwenden die Konvention der Nordhalbkugel."),
    # FAQ title
    ("Frequently asked questions", "H\u00e4ufig gestellte Fragen"),
    # FAQ visible accordion - 5 items
    ("<span>Why does the moon have phases?</span>", "<span>Warum hat der Mond Phasen?</span>"),
    ("<p class=\"mt-3 text-sm leading-relaxed text-slate-300\">The moon does not produce its own light - it reflects sunlight. As the moon orbits Earth, we see different fractions of its sunlit half, producing the phases. Half of the moon is always lit; the phase depends on how much of that lit half faces Earth.</p>",
     "<p class=\"mt-3 text-sm leading-relaxed text-slate-300\">Der Mond hat kein eigenes Licht - er reflektiert das Sonnenlicht. W\u00e4hrend der Mond die Erde umkreist, sehen wir verschiedene Anteile seiner beleuchteten H\u00e4lfte. Eine H\u00e4lfte des Mondes ist immer beleuchtet; die Phase h\u00e4ngt davon ab, wie viel davon der Erde zugewandt ist.</p>"),
    ("<span>How long is one full lunar cycle?</span>", "<span>Wie lange dauert ein kompletter Mondzyklus?</span>"),
    ("<p class=\"mt-3 text-sm leading-relaxed text-slate-300\">The synodic month - the time between two identical phases (e.g. full moon to full moon) - averages 29.53059 days (about 29 days, 12 hours, 44 minutes).</p>",
     "<p class=\"mt-3 text-sm leading-relaxed text-slate-300\">Der synodische Monat - die Zeit zwischen zwei gleichen Phasen (z. B. Vollmond zu Vollmond) - dauert durchschnittlich 29,53059 Tage (etwa 29 Tage, 12 Stunden, 44 Minuten).</p>"),
    ("<span>Why is a month 30 or 31 days but the lunar cycle 29.5?</span>", "<span>Warum hat ein Monat 30 oder 31 Tage, der Mondzyklus aber nur 29,5?</span>"),
    ("<p class=\"mt-3 text-sm leading-relaxed text-slate-300\">The Gregorian calendar is solar-based (365.2425 days per year). A lunar year of 12 synodic months is about 354.4 days - roughly 11 days shorter - which is why lunar calendars (e.g. the Islamic calendar) drift against the seasons unless intercalary months are added.</p>",
     "<p class=\"mt-3 text-sm leading-relaxed text-slate-300\">Der Gregorianische Kalender ist sonnenbasiert (365,2425 Tage pro Jahr). Ein Mondjahr aus 12 synodischen Monaten ist etwa 354,4 Tage lang - rund 11 Tage k\u00fcrzer. Deshalb verschieben sich Mondkalender (z. B. der islamische Kalender) gegen die Jahreszeiten, sofern keine Schaltmonate eingef\u00fcgt werden.</p>"),
    ("<span>What is the terminator?</span>", "<span>Was ist der Terminator?</span>"),
    ("<p class=\"mt-3 text-sm leading-relaxed text-slate-300\">The terminator is the boundary between the illuminated and dark parts of the moon's disc. Its curve (an ellipse as seen from Earth) gives each phase its distinctive shape - a thin ellipse for crescents, a straight line at the quarters, and a fat ellipse for gibbous phases.</p>",
     "<p class=\"mt-3 text-sm leading-relaxed text-slate-300\">Der Terminator ist die Grenze zwischen dem beleuchteten und dem dunklen Teil der Mondscheibe. Seine Kurve (von der Erde aus gesehen eine Ellipse) gibt jeder Phase ihre charakteristische Form - eine d\u00fcnne Ellipse f\u00fcr Sicheln, eine gerade Linie bei den Vierteln und eine fette Ellipse f\u00fcr die zunehmenden und abnehmenden Monde.</p>"),
    ("<span>Does the moon actually change shape?</span>", "<span>Ver\u00e4ndert der Mond wirklich seine Form?</span>"),
    ("<p class=\"mt-3 text-sm leading-relaxed text-slate-300\">No. The moon is always a sphere, and half of it is always sunlit. The apparent change in shape is only a change in the fraction of the sunlit half that faces Earth.</p>",
     "<p class=\"mt-3 text-sm leading-relaxed text-slate-300\">Nein. Der Mond ist immer eine Kugel, und eine H\u00e4lfte ist immer von der Sonne beleuchtet. Die scheinbare Form\u00e4nderung ist nur eine \u00c4nderung des Anteils der beleuchteten H\u00e4lfte, der der Erde zugewandt ist.</p>"),
    # related links
    ("Explore the lunar year", "Entdecken Sie das Mondjahr"),
    ('<a href="../moon-phases-2026.html" class="block rounded-2xl border border-white/10 bg-night-950/60 p-5 transition hover:border-moon-400/30">\n            <p class="text-sm font-semibold text-white">Moon Phases 2026</p>',
     '<a href="mondphasen-2026.html" class="block rounded-2xl border border-white/10 bg-night-950/60 p-5 transition hover:border-moon-400/30">\n            <p class="text-sm font-semibold text-white">Mondphasen 2026</p>'),
    ('<p class="mt-1 text-xs text-slate-400">Complete calendar, all 4 phases per month, UTC/CET.</p>',
     '<p class="mt-1 text-xs text-slate-400">Kompletter Kalender, alle 4 Phasen pro Monat, UTC/MEZ.</p>'),
    ('<p class="text-sm font-semibold text-white">Full Moon 2026</p>',
     '<p class="text-sm font-semibold text-white">Vollmond 2026</p>'),
    ('<p class="mt-1 text-xs text-slate-400">13 full moons, traditional names, dates.</p>',
     '<p class="mt-1 text-xs text-slate-400">13 Vollmonde, traditionelle Namen, Daten.</p>'),
    ('<p class="text-sm font-semibold text-white">New Moon 2026</p>',
     '<p class="text-sm font-semibold text-white">Neumond 2026</p>'),
    ('<p class="mt-1 text-xs text-slate-400">12 new moons, dates, meaning.</p>',
     '<p class="mt-1 text-xs text-slate-400">12 Neumonde, Daten, Bedeutung.</p>'),
    ('<p class="text-sm font-semibold text-white">Blue Moon 2026</p>',
     '<p class="text-sm font-semibold text-white">Blauer Mond 2026</p>'),
    ('<p class="mt-1 text-xs text-slate-400">What a blue moon is - and when the next one is.</p>',
     '<p class="mt-1 text-xs text-slate-400">Was ein blauer Mond ist - und wann der n\u00e4chste kommt.</p>'),
    ('<a href="blue-moon-2026.html"', '<a href="blauermond-2026.html"'),
    # CTA
    ("<h2 class=\"text-3xl font-bold tracking-tight text-white\">Get MondPlan</h2>",
     "<h2 class=\"text-3xl font-bold tracking-tight text-white\">MondPlan App laden</h2>"),
    ("<p class=\"mt-3 text-slate-300\">One-time purchase. No subscription. 100% on-device.</p>",
     "<p class=\"mt-3 text-slate-300\">Einmalkauf. Kein Abonnement. 100% lokal.</p>"),
    ("Get MondPlan App", "MondPlan App laden"),
    # footer
    ("&copy; 2026 100ideas. Sources: Meeus (1998), NASA.",
     "&copy; 2026 100ideas. Quellen: Meeus (1998), NASA."),
    ("<a href=\"../index.html\" class=\"transition hover:text-moon-300\">Home</a>",
     "<a href=\"index.html\" class=\"transition hover:text-moon-300\">Startseite</a>"),
    ("<a href=\"../privacy.html\" class=\"transition hover:text-moon-300\">Privacy</a>",
     "<a href=\"privacy.html\" class=\"transition hover:text-moon-300\">Datenschutz</a>"),
    ("<a href=\"../support.html\" class=\"transition hover:text-moon-300\">Support</a>",
     "<a href=\"support.html\" class=\"transition hover:text-moon-300\">Support</a>"),
    ("<a href=\"../moon-phases-2026.html\" class=\"transition hover:text-moon-300\">Moon Phases 2026</a>",
     "<a href=\"mondphasen-2026.html\" class=\"transition hover:text-moon-300\">Mondphasen 2026</a>"),
]


def main():
    html = open(EN, encoding="utf-8").read()
    applied = 0
    missing = []
    for en, de in TRANSLATIONS:
        if en in html:
            html = html.replace(en, de, 1)
            applied += 1
        else:
            missing.append(en[:60])
    os.makedirs(os.path.dirname(DE), exist_ok=True)
    open(DE, "w", encoding="utf-8").write(html)
    print(f"applied {applied}/{len(TRANSLATIONS)} translations")
    if missing:
        print("NOT FOUND (check these):")
        for m in missing:
            print(f"  - {m!r}")


if __name__ == "__main__":
    main()
