import threading
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, HTTPException

from src.pipeline.runner import run_pipeline
from src.spotify.auth import is_authenticated

router = APIRouter(prefix="/pipeline", tags=["pipeline"])

_lock = threading.Lock()
_status: dict = {"running": False, "last_run": None, "error": None}


def _run_in_background(recent: bool, top: bool, playlists: bool):
    global _status
    try:
        run_pipeline(recent=recent, top=top, playlists=playlists)
        _status["error"] = None
        _status["last_run"] = datetime.now(timezone.utc).isoformat()
    except Exception as e:
        _status["error"] = str(e)
    finally:
        _status["running"] = False


@router.post("/run")
def run(
    background_tasks: BackgroundTasks,
    recent: bool = True,
    top: bool = True,
    playlists: bool = False,
):
    if not is_authenticated():
        raise HTTPException(status_code=401, detail="Not authenticated with Spotify")
    if not _lock.acquire(blocking=False):
        raise HTTPException(status_code=409, detail="Pipeline is already running")
    _status["running"] = True
    _status["error"] = None
    _lock.release()
    background_tasks.add_task(_run_in_background, recent, top, playlists)
    return {"status": "accepted", "message": "Pipeline started"}


@router.get("/status")
def pipeline_status():
    return _status
