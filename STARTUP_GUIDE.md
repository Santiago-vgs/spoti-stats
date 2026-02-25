# Spoti Stats — Startup Guide

A data pipeline and dashboard for analyzing your Spotify listening habits.

**Stack:** Python (FastAPI, SQLAlchemy, SQLite) + Next.js (React, Recharts, Tailwind)

---

## Prerequisites

- **Python 3.11+** — [python.org/downloads](https://www.python.org/downloads/)
- **Node.js 18+** — [nodejs.org](https://nodejs.org/)
- **A Spotify account** (free or premium)

---

## Setup (5 steps)

### 1. Create a Spotify Developer App

1. Go to [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
2. Log in and click **Create App**
3. Fill in the form:
   - **App name:** Spoti Stats (or anything)
   - **App description:** Personal listening analytics
   - **Redirect URI:** `http://127.0.0.1:8000/callback`
   - **APIs used:** Check **Web API**
4. Click **Create**, then copy the **Client ID** and **Client Secret**

### 2. Set up the backend

```bash
cd backend
pip install -r requirements.txt
python scripts/setup.py
```

The setup script will prompt for your Client ID and Client Secret, then write the `.env` file for you.

### 3. Start the API server

```bash
python scripts/run_api.py
```

The API starts at **http://localhost:8000**.

### 4. Start the frontend

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

### 5. Sign in and sync

1. Open **http://localhost:3000**
2. Click **Sign in with Spotify** — authorize the app
3. Click **Sync Data** in the navbar — your data loads into the dashboard

That's it!

---

## Pages

| URL | What you'll see |
|-----|----------------|
| `/` | Dashboard with stat cards, listening timeline, top artists chart |
| `/history` | Paginated list of recently played tracks |
| `/top` | Top tracks and artists with time range selector, genre chart |
| `/playlists` | Browse your playlists and view their tracks |

---

## CLI Pipeline (optional)

You can also run the pipeline from the command line for cron jobs or automation:

```bash
cd backend
python scripts/run_pipeline.py              # Recent plays + top tracks/artists
python scripts/run_pipeline.py --playlists  # Also sync playlists
python scripts/run_pipeline.py --all        # Everything
```

---

## Troubleshooting

### "No module named 'src'"
Run scripts from the `backend/` directory, not from `backend/scripts/`.

### "INVALID_CLIENT: Invalid redirect URI"
Make sure the redirect URI in your Spotify Developer App settings **exactly matches:** `http://127.0.0.1:8000/callback`

### Frontend shows "Loading..." forever
1. Make sure the API server is running (`python scripts/run_api.py`)
2. Check the browser console for CORS or network errors

### Token expired
Delete the `.spotify_cache` file in the `backend/` directory and sign in again through the frontend.

---

## Project Structure

```
spoti_stats/
├── backend/
│   ├── .env                  # Your Spotify credentials (not in git)
│   ├── requirements.txt      # Python dependencies
│   ├── scripts/
│   │   ├── setup.py          # Interactive setup (writes .env)
│   │   ├── run_pipeline.py   # CLI data ingestion
│   │   └── run_api.py        # Start the FastAPI server
│   ├── src/
│   │   ├── config.py         # Settings from .env
│   │   ├── db/               # SQLAlchemy models + database setup
│   │   ├── spotify/          # Spotify auth + API wrapper
│   │   ├── pipeline/         # ETL: ingest → transform → load
│   │   └── api/              # FastAPI routes + schemas
│   └── data/
│       └── spoti_stats.db    # SQLite database (not in git)
├── frontend/
│   ├── app/                  # Next.js pages
│   ├── components/           # React components (charts, UI)
│   └── lib/                  # API client + TypeScript types
└── .gitignore
```
