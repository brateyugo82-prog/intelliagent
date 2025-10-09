"""
✅ FASTAPI BACKEND ENTRY POINT (FINAL + STABLE)
------------------------------------------------
Verknüpft:
- Agenten-Workflow /api/workflow/start
- Meta-Webhook /meta/webhook
- IntelliAgent-Pipeline /pipeline/meta_event
- Kostenstatistik /api/stats/costs
Render-ready & lokal via Uvicorn startbar.
"""

import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# 🔹 interne Module
from backend.master_agent.master import run_workflow
from backend.core.logger import logger
from backend.api.pipeline_manager import router as pipeline_router
from backend.api.stats import router as stats_router   # <-- Import bleibt oben

# ============================================
# 📂 Basisverzeichnisse
# ============================================
BASE_DIR = Path(__file__).resolve().parents[1]  # backend/
CLIENTS_DIR = BASE_DIR / "clients"
CLIENTS_DIR.mkdir(parents=True, exist_ok=True)

# ============================================
# ⚙️ FastAPI App
# ============================================
app = FastAPI(title="IntelliAgent Backend", version="2.0")

# CORS für Frontend-Kommunikation
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static Files (z. B. Bilder aus DesignAgent unter /static/<client>/output/*.png)
app.mount("/static", StaticFiles(directory=str(CLIENTS_DIR)), name="static")

# ============================================
# 📦 Models
# ============================================
class WorkflowRequest(BaseModel):
    client: str
    prompt: str
    platform: str | None = None


# ============================================
# 🌐 Routes
# ============================================

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Dummy-Favicon, um 404 zu vermeiden."""
    icon_path = BASE_DIR / "static" / "favicon.ico"
    if icon_path.exists():
        return FileResponse(str(icon_path))
    return Response(status_code=204)


@app.get("/")
async def root():
    """Health Check für Render."""
    return {"status": "ok", "message": "IntelliAgent Backend läuft 🚀"}


@app.post("/api/workflow/start")
async def start_workflow(req: WorkflowRequest):
    """Manueller Start eines Agenten-Workflows (z. B. per Frontend-Button)."""
    platform = req.platform if req.platform else ""
    result = run_workflow(req.client, req.prompt, platform)
    return {"status": "ok", "client": req.client, "platform": platform, "result": result}


@app.get("/api/clients")
async def get_clients():
    """Listet alle verfügbaren Clients mit config.json auf."""
    clients = []
    for entry in CLIENTS_DIR.iterdir():
        if (entry / "config.json").is_file():
            clients.append(entry.name)
    return {"clients": clients}


# ============================================
# 🧩 Router registrieren (NACH App-Definition!)
# ============================================
app.include_router(pipeline_router)
app.include_router(stats_router)

# ============================================
# 🚀 Lokaler Start (nur für Dev)
# ============================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.core.main:app", host="0.0.0.0", port=8000, reload=True)
