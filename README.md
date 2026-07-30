# SitesTrack

A lightweight, self-hosted website analytics tracker built with Flask and SQLite. It collects visit events from one or more sites via a simple HTTP endpoint and displays the results on a dashboard with charts.

## Features

- **Visit tracking endpoint** (`POST /track`) — records a visit for a given site name and category, capturing IP address, user agent, and a basic device classification (Mobile / Tablet / Desktop).
- **Multi-site support** — sites are created automatically on first visit and grouped by category.
- **Analytics dashboard** (`GET /dashboard`) — a dark-themed page showing:
  - KPI cards: total visits, visits today, unique sites tracked, top site, and average visits per site.
  - Site performance bar chart (visits per site).
  - Device breakdown pie chart (Mobile / Tablet / Desktop).
  - Country breakdown pie chart (currently a placeholder — country is not yet resolved from IP).
  - Hourly traffic line chart.
- **SQLite storage** — data persists in a local `sitestrack.db` file with `sites` and `visits` tables, created automatically on startup.

## Tech stack

- **Backend:** Python, Flask
- **Database:** SQLite (via the standard library `sqlite3` module)
- **Frontend:** Server-rendered Jinja2 template (`templates/dashboard.html`) with [Chart.js](https://www.chartjs.org/) (loaded from CDN) for charts, plus a custom stylesheet (`static/css/style.css`)

## Project structure

```
app.py                  # Flask app: DB init, /track and /dashboard routes
requirements.txt        # Python dependencies
templates/dashboard.html  # Analytics dashboard UI
static/css/style.css      # Dashboard styling
sitestrack.db            # SQLite database (auto-created, git-ignored)
```

## Setup

```bash
git clone https://github.com/Luke-Manyamazi/SitesTrack.git
cd SitesTrack
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

## Running

```bash
python app.py
```

This starts the Flask development server (debug mode) on `http://127.0.0.1:5000` and initializes `sitestrack.db` if it doesn't already exist.

- `http://127.0.0.1:5000/` — basic health check text
- `http://127.0.0.1:5000/dashboard` — analytics dashboard

## Sending a test visit

```bash
curl -X POST http://127.0.0.1:5000/track \
  -H "Content-Type: application/json" \
  -d '{"site": "example.com", "category": "blog"}'
```

## Notes

- Country detection is a placeholder (`"Unknown"`) — no IP geolocation lookup is wired in yet.
- This is a development setup (`debug=True`); it is not configured for production deployment as-is.
