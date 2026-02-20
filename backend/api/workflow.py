from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from master_agent.master import run_workflow
from core.logger import logger

router = APIRouter(prefix="/api/workflow", tags=["workflow"])


# -------------------------------------------------
# 📦 REQUEST MODEL
# -------------------------------------------------
class WorkflowRequest(BaseModel):
    client: str
    mode: Optional[str] = "single"          # single | today | week | foundation
    content_category: Optional[str] = None


# -------------------------------------------------
# 🚀 START WORKFLOW
# -------------------------------------------------
@router.post("/start")
def start_workflow(req: WorkflowRequest) -> Dict[str, Any]:
    """
    Modes:
    - single      → einzelner Post (mit content_category)
    - today       → heutiger Tag aus weekly_plan.json
    - week        → komplette Woche aus weekly_plan.json
    - foundation  → Pre-Launch / Foundation (komplett im Master Agent)
    """

    logger.info(
        "[API][WORKFLOW] Start | "
        f"client={req.client} | "
        f"mode={req.mode} | "
        f"content_category={req.content_category}"
    )

    try:
        # -------------------------------------------------
        # 🟣 FOUNDATION MODE
        # -------------------------------------------------
        if req.mode == "foundation":
            result = run_workflow(
                client=req.client,
                mode="foundation",
            )

        # -------------------------------------------------
        # 🔵 NORMAL MODES (single / today / week)
        # -------------------------------------------------
        else:
            result = run_workflow(
                client=req.client,
                mode=req.mode or "single",
                content_category=req.content_category,
            )

        logger.info("[API][WORKFLOW] Erfolgreich")

        return {
            "status": "ok",
            "client": req.client,
            "mode": req.mode,
            "result": result,
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.exception("[API][WORKFLOW] Fehler im Workflow")
        raise HTTPException(status_code=500, detail=str(e))