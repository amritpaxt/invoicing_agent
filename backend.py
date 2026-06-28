from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from main import app as api_app

BASE_DIR = Path(__file__).resolve().parent
TIA_HTML = BASE_DIR / "TIA.html"

app = FastAPI(title="TIA - Touchless Invoice Agent")
app.mount("/api", api_app)

@app.get("/")
def index():
    if not TIA_HTML.exists():
        return {
            "status": "ok",
            "message": "TIA backend is running but TIA.html is missing.",
            "api": "/api",
        }
    return FileResponse(TIA_HTML)


@app.get("/{path_name:path}")
def spa_fallback(path_name: str):
    if path_name.startswith("api"):
        raise HTTPException(status_code=404, detail="Not found")

    candidate = BASE_DIR / path_name
    if candidate.is_file():
        return FileResponse(candidate)

    if TIA_HTML.exists():
        return FileResponse(TIA_HTML)

    raise HTTPException(status_code=404, detail="Not found")
