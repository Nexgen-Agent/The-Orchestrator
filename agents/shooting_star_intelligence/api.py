from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from agents.shooting_star_intelligence.intelligence import ShootingStarIntelligence

router = APIRouter(prefix="/shooting-star-intelligence", tags=["shooting-star-intelligence"])

@router.post("/track")
async def track_progress(payload: Dict[str, Any]):
    agent_name = payload.get("agent_name")
    capability = payload.get("capability")
    if not agent_name or capability is None:
        raise HTTPException(status_code=400, detail="Missing agent_name or capability")

    try:
        engine = ShootingStarIntelligence()
        progress = await engine.track_progress(agent_name, float(capability))
        return {"status": "success", "result": progress.model_dump(mode='json')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/audit")
async def perform_audit(payload: Dict[str, Any]):
    agent_name = payload.get("agent_name")
    project_path = payload.get("project_path")
    if not agent_name or not project_path:
        raise HTTPException(status_code=400, detail="Missing agent_name or project_path")

    try:
        engine = ShootingStarIntelligence()
        report = await engine.perform_readiness_audit(agent_name, project_path)
        return {"status": "success", "result": report.model_dump(mode='json')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard")
async def get_readiness_dashboard():
    try:
        engine = ShootingStarIntelligence()
        return {"status": "success", "readiness": engine.readiness.model_dump(mode='json')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
