# Hinweis: Absolute Imports (backend.*) für Render + lokale Uvicorn-Kompatibilität
"""
FastAPI Backend Entry Point
"""
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.master_agent.master import run_workflow
from backend.core.logger import logger  # Logging-Konfiguration und logger

# Basisverzeichnisse
BASE_DIR = Path(__file__).resolve().parents[1]  # backend/
CLIENTS_DIR = BASE_DIR / "clients"
CLIENTS_DIR.mkdir(parents=True, exist_ok=True)  # falls nicht vorhanden

# FastAPI App
app = FastAPI(title="Agenten Backend", version="1.0.0")

# CORS (für Frontend-Kommunikation)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static Files (z. B. Bilder aus DesignAgent unter /static/<client>/output/*.png)
app.mount("/static", StaticFiles(directory=str(CLIENTS_DIR)), name="static")


class WorkflowRequest(BaseModel):
    client: str
    prompt: str
    platform: str | None = None


# Dummy-Favicon-Endpoint, damit Browser keine 404-Fehler spammen
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    icon_path = BASE_DIR / "static" / "favicon.ico"
    if icon_path.exists():
        return FileResponse(str(icon_path))
    return Response(status_code=204)


@app.get("/")
async def root():
    """Gesundheitscheck-Endpoint."""
    return {"status": "ok", "message": "Backend läuft 🚀"}


@app.post("/api/workflow/start")
async def start_workflow(req: WorkflowRequest):
    """
    Startet den Workflow für einen Client mit Prompt und Platform.
    - client: Name des Clients (z.B. 'mtm')
    - prompt: Freitext, der an die Agenten übergeben wird
    - platform: Zielplattform (optional)
    """
    platform = req.platform if req.platform else ""
    result = run_workflow(req.client, req.prompt, platform)
    return {"status": "ok", "client": req.client, "platform": platform, "result": result}


@app.get("/api/clients")
async def get_clients():
    """
    Listet alle verfügbaren Clients auf, die eine config.json enthalten.
    """
    clients = []
    for entry in CLIENTS_DIR.iterdir():
        config_path = entry / "config.json"
        if config_path.is_file():
            clients.append(entry.name)
    return {"clients": clients}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.core.main:app", host="0.0.0.0", port=8000, reload=True)
