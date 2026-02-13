from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from agents.self_evolution_engine.engine import SelfEvolutionEngine

router = APIRouter(prefix="/self-evolution", tags=["self-evolution"])

@router.post("/optimize")
async def run_optimization(payload: Dict[str, Any]):
    project_path = payload.get("project_path")
    if not project_path:
        raise HTTPException(status_code=400, detail="Missing project_path")

    try:
        engine = SelfEvolutionEngine()
        report = await engine.run_optimization_cycle(project_path)
        return {"status": "success", "result": report.model_dump(mode='json')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audit")
async def get_evolution_history():
    try:
        engine = SelfEvolutionEngine()
        return {"status": "success", "history": engine.history.model_dump(mode='json')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
