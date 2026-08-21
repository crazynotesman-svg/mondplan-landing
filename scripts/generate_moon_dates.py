"""Generate the 2026 moon phase dates (new / first quarter / full / last quarter)
using Jean Meeus, "Astronomical Algorithms" ch.49 (phases of the moon).

Precision: main correction terms only -> about +/- 1-2 minutes.
Output: data/moon-phases-2026.json (UTC instants) and prints the table for
embedding into the landing pages.

Usage: python scripts/generate_moon_dates.py
"""
import json
import math
import os
import sys

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

# Reference: k=0 -> new moon 2000-01-06 18:14 UTC (JD 2451550.09766)
REF_JD = 2451550.09766
SYN = 29.530588861


def jd_to_utc(jd):
    """Julian Date (UT) -> (year, month, day, hour, minute) as UTC."""
    jd += 0.5  # shift to midnight-based
    z = int(jd)
    f = jd - z
    if z < 2299161:
        a = z
    else:
        alpha = int((z - 1867216.25) / 36524.25)
        a = z + 1 + alpha - int(alpha / 4)
    b = a + 1524
    c = int((b - 122.1) / 365.25)
    d = int(365.25 * c)
    e = int((b - d) / 30.6001)
    day = b - d - int(30.6001 * e) + f
    month = e - 1 if e < 14 else e - 13
    year = c - 4716 if month > 2 else c - 4715
    dd = int(day)
    frac = day - dd
    total_min = int(round(frac * 1440))
    hour = total_min // 60
    minute = total_min % 60
    return year, month, dd, hour, minute


def utc_to_cest(dt):
    """UTC (year, month, day, hour, minute) -> Central European Time string.
    DST (CEST, +2) from last Sunday of March to last Sunday of October.
    """
    y, m, d, hh, mm = dt
    # last Sunday of March
    import datetime
    mar = datetime.date(y, 3, 31)
    mar_sun = mar - datetime.timedelta(days=(mar.weekday() + 1) % 7)
    oct_ = datetime.date(y, 10, 31)
    oct_sun = oct_ - datetime.timedelta(days=(oct_.weekday() + 1) % 7)
    date = datetime.date(y, m, d)
    offset = 2 if mar_sun <= date <= oct_sun else 1
    mins = hh * 60 + mm + offset * 60
    hh2, mm2 = divmod(mins % 1440, 60)
    return y, m, d, hh2, mm2, offset


def phases_for_year(year, quarter=True):
    """Return list of dicts: {k, phase, jd, utc, cet} for the year."""
    # k for new moons around the year
    k0 = int(round((year - 2000) * 12.3685))
    # scan k range that covers the year
    results = []
    # find new-moon k indexes; start from k0-3 (covers Jan) to k0+14 (covers Dec+)
    for kk in range(k0 - 3, k0 + 15):
        for offset, phase in ((0.0, "new"), (0.25, "first-quarter"),
                              (0.5, "full"), (0.75, "last-quarter")):
            if not quarter and offset not in (0.0, 0.5):
                continue
            k = kk + offset
            t = k / 1236.85
            jde = (REF_JD + SYN * k
                   + 0.00015437 * t ** 2
                   - 0.000000150 * t ** 3
                   + 0.00000000073 * t ** 4)
            e = 1 - 0.002516 * t - 0.0000074 * t ** 2
            m = math.radians(2.5534 + 29.10535670 * k
                             - 0.0000014 * t ** 2 - 0.00000011 * t ** 3)
            mp = math.radians(201.5643 + 385.81693528 * k
                              + 0.0107582 * t ** 2 + 0.00001238 * t ** 3
                              - 0.000000058 * t ** 4)
            f = math.radians(160.7108 + 390.67050284 * k
                             - 0.0016118 * t ** 2 - 0.00000227 * t ** 3
                             + 0.000000011 * t ** 4)
            omega = math.radians(124.7746 - 1.56375588 * k
                                 + 0.0020672 * t ** 2 + 0.00000215 * t ** 3)
            # main correction terms (Meeus 49.A, new/full) / (49.B, quarters)
            if phase in ("new", "full"):
                dj = (-0.40720 * math.sin(mp)
                      + 0.17241 * e * math.sin(m)
                      + 0.01608 * math.sin(2 * mp)
                      + 0.01039 * math.sin(2 * f)
                      + 0.00739 * e * math.sin(mp - m)
                      - 0.00514 * e * math.sin(mp + m)
                      + 0.00208 * e * e * math.sin(2 * m)
                      - 0.00111 * math.sin(mp - 2 * f)
                      - 0.00057 * math.sin(mp + 2 * f)
                      + 0.00056 * e * math.sin(2 * mp + m)
                      - 0.00042 * math.sin(3 * mp)
                      + 0.00042 * e * math.sin(m + 2 * f)
                      + 0.00038 * e * math.sin(m - 2 * f)
                      - 0.00024 * e * math.sin(2 * mp - m)
                      - 0.00017 * math.sin(omega))
            else:
                dj = (-0.62801 * math.sin(mp)
                      + 0.17172 * e * math.sin(m)
                      - 0.01183 * e * math.sin(mp + m)
                      + 0.00862 * math.sin(2 * mp)
                      + 0.00804 * math.sin(2 * f)
                      + 0.00454 * e * math.sin(mp - m)
                      + 0.00204 * e * e * math.sin(2 * m)
                      - 0.00180 * math.sin(mp - 2 * f)
                      - 0.00070 * math.sin(mp + 2 * f)
                      - 0.00040 * math.sin(3 * mp)
                      - 0.00034 * e * math.sin(2 * mp - m)
                      + 0.00032 * e * math.sin(m + 2 * f)
                      + 0.00032 * e * math.sin(m - 2 * f)
                      - 0.00028 * e * e * math.sin(mp + m)
                      + 0.00027 * e * math.sin(2 * mp + m)
                      - 0.00017 * math.sin(omega))
            jd = jde + dj
            utc = jd_to_utc(jd)
            y, m_, d_, h, mi = utc
            if y == year:
                cet = utc_to_cest(utc)
                results.append({
                    "phase": phase,
                    "k": round(k, 2),
                    "utc": f"{y}-{m_:02d}-{d_:02d} {h:02d}:{mi:02d}",
                    "cet": f"{cet[0]}-{cet[1]:02d}-{cet[2]:02d} {cet[3]:02d}:{cet[4]:02d}",
                    "cest": cet[5],
                })
    results.sort(key=lambda r: r["utc"])
    return results


def main():
    year = 2026
    phases = phases_for_year(year)
    os.makedirs(DATA_DIR, exist_ok=True)
    out = os.path.join(DATA_DIR, "moon-phases-2026.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(phases, f, ensure_ascii=False, indent=1)
    print(f"wrote {out}  ({len(phases)} entries)")

    # table preview by month
    print()
    print("month | new moon (CET) | first q | full moon (CET) | last q")
    from collections import defaultdict
    by_month = defaultdict(list)
    for p in phases:
        by_month[p["cet"][5:7]].append(p)
    for mm in sorted(by_month):
        row = by_month[mm]
        def pick(ph):
            for p in row:
                if p["phase"] == ph:
                    return p["cet"][5:]
            return "-"
        print(f"{mm:>5} | {pick('new'):>16} | {pick('first-quarter'):>9} | {pick('full'):>16} | {pick('last-quarter'):>8}")

    # cross-check against known 2026 events (NASA eclipse page)
    print()
    print("=== cross-check with known 2026 events ===")
    known = [
        ("new", "2026-02-17", "solar annular eclipse (new moon)"),
        ("full", "2026-03-03", "total lunar eclipse (full moon)"),
        ("new", "2026-08-12", "total solar eclipse (new moon)"),
        ("full", "2026-08-28", "partial lunar eclipse (full moon)"),
    ]
    for ph, date, note in known:
        for p in phases:
            if p["phase"] == ph and p["utc"][:10] == date:
                print(f"  MATCH {ph:12s} {date}  {p['utc']} UTC  ({note})")


if __name__ == "__main__":
    main()
