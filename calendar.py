#!/usr/bin/env python3
"""
Flarient Space Calendar — .ICS Generator

Regenerates flarient-space-calendar.ics with:
- Meteor showers
- Eclipses (solar and lunar)
- Planetary events (conjunctions, oppositions)
- Selected launches
- Major astronomical events

Users subscribe once → Flarient lives permanently in their calendar.
"""

import os, sys, json, datetime, textwrap
from pathlib import Path
import requests

FLARIENT_API = os.environ.get("FLARIENT_API_URL", "https://flarient.com").rstrip("/")
REPO_DIR = Path(os.environ.get("GITHUB_WORKSPACE", "."))
ICS_FILE = REPO_DIR / "flarient-space-calendar.ics"

CALENDAR_NAME = "Flarient Space Calendar"
CALENDAR_DESC = "Meteor showers, eclipses, planetary events, launches, and major astronomical events. Powered by Flarient — the space weather intelligence platform."
CALENDAR_URL = "https://flarient.com/space-calendar"


def log(msg):
    print(f"[calendar] {msg}", flush=True)


# ── ICS formatting ────────────────────────────────────────────────────────
def format_dt(dt):
    """Format datetime as ICS UTC timestamp: YYYYMMDDTHHMMSSZ"""
    if isinstance(dt, str):
        try:
            dt = datetime.datetime.fromisoformat(dt.replace("Z", "+00:00"))
        except:
            return ""
    return dt.strftime("%Y%m%dT%H%M%SZ")


def escape_ics(text):
    """Escape special characters for ICS format."""
    if not text:
        return ""
    return (text
            .replace("\\", "\\\\")
            .replace(";", "\\;")
            .replace(",", "\\,")
            .replace("\n", "\\n")
            .replace("\r", ""))


def make_event(uid, title, description, start_dt, end_dt, url=None, all_day=False):
    """Create an ICS VEVENT string."""
    dtstart = format_dt(start_dt)
    dtend = format_dt(end_dt)
    if all_day:
        dtstart = start_dt.strftime("%Y%m%d") if isinstance(start_dt, datetime.datetime) else start_dt[:10]
        dtend = (end_dt if isinstance(end_dt, datetime.datetime) else datetime.datetime.fromisoformat(end_dt)).strftime("%Y%m%d") if end_dt else dtstart

    lines = [
        "BEGIN:VEVENT",
        f"UID:{uid}@flarient.com",
        f"DTSTAMP:{format_dt(datetime.datetime.now(datetime.timezone.utc))}",
        f"DTSTART{';VALUE=DATE' if all_day else ''}:{dtstart}",
    ]
    if dtend:
        lines.append(f"DTEND{';VALUE=DATE' if all_day else ''}:{dtend}")
    lines.append(f"SUMMARY:{escape_ics(title)}")
    if description:
        lines.append(f"DESCRIPTION:{escape_ics(description)}")
    if url:
        lines.append(f"URL:{url}")
    lines.append("END:VEVENT")
    return "\n".join(lines)


# ── Fetch events from Flarient ────────────────────────────────────────────
def fetch_events():
    """Fetch all calendar-worthy events from Flarient API."""
    log("Fetching events from Flarient API...")
    events = []
    try:
        resp = requests.get(f"{FLARIENT_API}/api/functions/getSpaceCalendarEvents", timeout=30)
        resp.raise_for_status()
        data = resp.json()
        events = data.get("events", [])
        log(f"  {len(events)} events from Flarient API")
    except Exception as e:
        log(f"  API fetch failed: {e}, using static data")

    # Always include static astronomical events as fallback/supplement
    events.extend(get_static_events())
    return events


def get_static_events():
    """Static astronomical events that don't change (meteor showers, known eclipses)."""
    now = datetime.datetime.now(datetime.timezone.utc)
    year = now.year

    static = []

    # Major meteor showers (peak dates — approximate, recurring annually)
    meteor_showers = [
        ("Quadrantids", f"{year}-01-03", f"{year}-01-04"),
        ("Lyrids", f"{year}-04-22", f"{year}-04-23"),
        ("Eta Aquariids", f"{year}-05-06", f"{year}-05-07"),
        ("Perseids", f"{year}-08-12", f"{year}-08-13"),
        ("Draconids", f"{year}-10-08", f"{year}-10-09"),
        ("Orionids", f"{year}-10-21", f"{year}-10-22"),
        ("Taurids", f"{year}-11-05", f"{year}-11-06"),
        ("Leonids", f"{year}-11-17", f"{year}-11-18"),
        ("Geminids", f"{year}-12-13", f"{year}-12-14"),
        ("Ursids", f"{year}-12-22", f"{year}-12-23"),
    ]
    for name, start, end in meteor_showers:
        static.append({
            "uid": f"meteor-{name.lower()}-{year}",
            "title": f"{name} Meteor Shower Peak",
            "description": f"The {name} meteor shower peaks tonight. Best viewing after midnight, away from city lights. Check flarient.com for aurora and space weather conditions that may affect visibility.",
            "start": start,
            "end": end,
            "all_day": True,
            "url": f"{FLARIENT_API}/space-calendar",
        })

    # Known eclipses (extend as they're announced)
    # These are approximate — real eclipse data should come from the API
    # 2026 total solar eclipse (August 12, 2026 — visible in Greenland, Iceland, Spain)
    if year == 2026:
        static.append({
            "uid": f"eclipse-solar-2026-08-12",
            "title": "Total Solar Eclipse (Greenland, Iceland, Spain)",
            "description": "Total solar eclipse visible from Greenland, Iceland, and northern Spain. Partial eclipse visible from much of Europe and North America. Check flarient.com for space weather conditions.",
            "start": "2026-08-12",
            "end": "2026-08-12",
            "all_day": True,
            "url": f"{FLARIENT_API}/space-calendar",
        })

    # 2026 lunar eclipse (February 17, 2026 — penumbral)
    if year >= 2026:
        static.append({
            "uid": f"eclipse-lunar-2026-02-17",
            "title": "Penumbral Lunar Eclipse",
            "description": "Penumbral lunar eclipse visible from the Americas, Europe, and Africa. The Moon passes through Earth's penumbral shadow.",
            "start": "2026-02-17",
            "end": "2026-02-17",
            "all_day": True,
            "url": f"{FLARIENT_API}/space-calendar",
        })

    return static


# ── Generate ICS file ─────────────────────────────────────────────────────
def generate_ics(events):
    log(f"Generating ICS file with {len(events)} events...")

    # Deduplicate by UID
    seen = set()
    unique_events = []
    for e in events:
        uid = e.get("uid") or f"event-{hash(e.get('title', ''))}"
        if uid not in seen:
            seen.add(uid)
            e["uid"] = uid
            unique_events.append(e)

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Flarient//Space Calendar//EN",
        f"X-WR-CALNAME:{escape_ics(CALENDAR_NAME)}",
        f"X-WR-CALDESC:{escape_ics(CALENDAR_DESC)}",
        "X-WR-TIMEZONE:UTC",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
    ]

    for e in unique_events:
        try:
            start_str = e.get("start") or e.get("start_time") or e.get("date")
            end_str = e.get("end") or e.get("end_time") or start_str
            all_day = e.get("all_day", False)

            if not start_str:
                continue

            # Parse dates
            if "T" in str(start_str):
                start_dt = datetime.datetime.fromisoformat(start_str.replace("Z", "+00:00"))
            else:
                start_dt = datetime.datetime.fromisoformat(start_str + "T00:00:00+00:00")

            if end_str and "T" in str(end_str):
                end_dt = datetime.datetime.fromisoformat(end_str.replace("Z", "+00:00"))
            elif end_str:
                end_dt = datetime.datetime.fromisoformat(end_str + "T23:59:00+00:00")
            else:
                end_dt = start_dt + datetime.timedelta(hours=1)

            uid = e.get("uid", f"event-{hash(e.get('title', ''))}")
            title = e.get("title", "Space Event")
            desc = e.get("description") or e.get("summary") or e.get("current_summary", "")
            url = e.get("url") or f"{FLARIENT_API}/space-calendar"

            # Add Flarient branding to description
            if "flarient.com" not in (desc or "").lower():
                desc = f"{desc}\n\nPowered by Flarient — https://flarient.com"

            lines.append(make_event(uid, title, desc, start_dt, end_dt, url, all_day))
        except Exception as ex:
            log(f"  Skipping event '{e.get('title', '?')}': {ex}")

    lines.append("END:VCALENDAR")

    ics_content = "\r\n".join(lines) + "\r\n"
    ICS_FILE.write_text(ics_content, encoding="utf-8")
    log(f"  ICS file written: {ICS_FILE} ({len(unique_events)} events)")


def main():
    log("=== Flarient Space Calendar Generator ===")
    events = fetch_events()
    generate_ics(events)
    log("Done")


if __name__ == "__main__":
    main()
