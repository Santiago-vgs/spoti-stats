from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from src.api.routers import artists, auth, decades, history, insights, pipeline, playlists, stats, tracks
from src.db.init_db import create_tables
from src.spotify.auth import exchange_code

app = FastAPI(title="Spoti Stats API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(pipeline.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(tracks.router, prefix="/api")
app.include_router(artists.router, prefix="/api")
app.include_router(stats.router, prefix="/api")
app.include_router(playlists.router, prefix="/api")
app.include_router(insights.router, prefix="/api")
app.include_router(decades.router, prefix="/api")


@app.on_event("startup")
def on_startup():
    create_tables()


@app.get("/")
def root():
    return RedirectResponse("/docs")


@app.get("/callback")
def spotify_callback(code: str):
    exchange_code(code)
    return RedirectResponse("http://localhost:3000")


@app.get("/api/health")
def health():
    return {"status": "ok"}
