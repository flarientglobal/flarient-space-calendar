# Flarient Space Calendar

An open `.ICS` calendar with meteor showers, eclipses, planetary events, missions, and major astronomical events. Users subscribe once — Flarient lives permanently in their calendar.

## Subscribe

### One-click subscription

**Webcal link (auto-adds to your calendar):**

\`\`\`
webcal://flarientglobal.github.io/flarient-space-calendar/flarient-space-calendar.ics
\`\`\`

### Manual subscription

1. Copy the URL: `https://flarientglobal.github.io/flarient-space-calendar/flarient-space-calendar.ics`
2. Open your calendar app (Google Calendar, Apple Calendar, Outlook)
3. Add calendar by URL → paste the link
4. Done — events update automatically

### Google Calendar
1. Go to [calendar.google.com](https://calendar.google.com)
2. Settings → Add calendar → From URL
3. Paste: `https://flarientglobal.github.io/flarient-space-calendar/flarient-space-calendar.ics`

### Apple Calendar
1. File → New Calendar Subscription
2. Paste: `webcal://flarientglobal.github.io/flarient-space-calendar/flarient-space-calendar.ics`

### Outlook
1. Open Outlook → Add calendar → Subscribe from web
2. Paste: `https://flarientglobal.github.io/flarient-space-calendar/flarient-space-calendar.ics`

## What's included

- ☄️ **Meteor showers** — Quadrantids, Lyrids, Perseids, Geminids, and more
- 🌑 **Eclipses** — Solar and lunar eclipses with visibility regions
- 🪐 **Planetary events** — Conjunctions, oppositions, and close approaches
- 🚀 **Selected launches** — Major space missions and launches
- 🌌 **Major astronomical events** — Comets, transits, and rare phenomena

Each event includes a link back to [flarient.com](https://flarient.com) for detailed space weather conditions and forecasts.

## How it works

- A GitHub Action runs daily at 01:00 UTC
- Fetches events from the Flarient API and static astronomical data
- Regenerates the `.ICS` file
- Commits to the repository
- GitHub Pages serves the file at a permanent URL

## Cost

**Free** — runs on GitHub Actions, served via GitHub Pages.

## About

Built by [Flarient](https://flarient.com) — the space weather intelligence platform.

## License

MIT — the calendar data is open and free to use.
