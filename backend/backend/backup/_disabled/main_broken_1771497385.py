"""
✅ FASTAPI BACKEND ENTRY POINT (FINAL + STABLE)
"""

from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

# ============================================================
# 📂 BASISVERZEICHNISSE
# ============================================================

CURRENT_FILE = Path(__file__).resolve()

BACKEND_DIR = CURRENT_FILE
while BACKEND_DIR.name != "backend":
    BACKEND_DIR = BACKEND_DIR.parent

CLIENTS_DIR = BACKEND_DIR / "clients"
CLIENTS_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# ⚙️ FASTAPI APP
# ============================================================

app = FastAPI(
    title="IntelliAgent Backend",
    version="2.0",
)

# ============================================================
# 🌍 CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# 🖼 STATIC FILES
# ============================================================

app.mount(
    "/static",
    StaticFiles(directory=CLIENTS_DIR),
    name="static",
)

# ============================================================
# 🔎 DEBUG ENDPOINT
# ============================================================

@app.get("/debug/static")
def debug_static():
    return {
        "backend_dir": str(BACKEND_DIR),
        "clients_dir": str(CLIENTS_DIR),
        "clients_dir_exists": CLIENTS_DIR.exists(),
        "mtm_client_exists": (CLIENTS_DIR / "mtm_client").exists(),
        "preview_dir_exists": (
            CLIENTS_DIR / "mtm_client" / "output" / "preview"
        ).exists(),
        "posting_queue_exists": (
            CLIENTS_DIR / "mtm_client" / "output" / "posting_queue"
        ).exists(),
    }

# ============================================================
# 🔹 ROUTER IMPORTS
from api.leads import router as leads_router
from api.leads_meta import router as leads_meta_router
from api.stats import router as stats_router
from api.dashboard import router as dashboard_router
from api.workflow import router as workflow_router
from api.publisher import router as publisher_router
from api.foundation_create_previews import router as foundation_previews_router
from api.foundation_autoschedule import router as foundation_autoschedule_router
# ============================================================

from api.leads_meta import router as leads_meta_router
from api.stats import router as stats_router

from api.dashboard import router as dashboard_router
from api.workflow import router as workflow_router
from api.publisher import router as publisher_router

from api.foundation_create_previews import router as foundation_previews_router
from api.foundation_autoschedule import router as foundation_autoschedule_router

# ============================================================
# 🧩 ROUTER REGISTRIEREN
app.include_router(leads_router)
app.include_router(leads_meta_router)
app.include_router(stats_router)
app.include_router(dashboard_router)
app.include_router(workflow_router)
app.include_router(publisher_router)
app.include_router(foundation_previews_router)
app.include_router(foundation_autoschedule_router)
# ============================================================


# 🔹 LEADS
app.include_router(leads_router)
app.include_router(leads_meta_router)

# 🔹 STATS
app.include_router(stats_router)

# 🔹 CORE SYSTEM
app.include_router(dashboard_router)
app.include_router(workflow_router)
app.include_router(publisher_router)

# 🔹 FOUNDATION
app.include_router(foundation_previews_router)
app.include_router(foundation_autoschedule_router)
# 🔹 LEADS

# 🔹 STATS

# 🔹 CORE SYSTEM

# 🔹 FOUNDATION

# ============================================================
# 🌐 HEALTH
# ============================================================

@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "IntelliAgent Backend läuft 🚀",
    }

# ============================================================
# 🖼 FAVICON
# ============================================================

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    icon_path = BACKEND_DIR / "public" / "favicon.ico"
    if icon_path.exists():
        return FileResponse(str(icon_path))
    return Response(status_code=204)
