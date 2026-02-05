from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from agents.meta_agent_trainer.engine import MetaAgentTrainerEngine
from agents.meta_agent_trainer.models import AgentBlueprint

router = APIRouter(prefix="/mate", tags=["mate"])

@router.post("/generate")
async def generate_agent(payload: Dict[str, Any]):
    try:
        blueprint = AgentBlueprint(**payload)
        engine = MetaAgentTrainerEngine()
        agent_dir = engine.generate_agent_from_blueprint(blueprint)
        return {"status": "success", "agent_dir": agent_dir}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/train")
async def train_agent(payload: Dict[str, Any]):
    agent_name = payload.get("agent_name")
    project_path = payload.get("project_path")
    if not agent_name or not project_path:
        raise HTTPException(status_code=400, detail="Missing agent_name or project_path")

    try:
        engine = MetaAgentTrainerEngine()
        report = await engine.simulate_training(agent_name, project_path)
        return {"status": "success", "result": report.model_dump(mode='json')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audit")
async def get_mate_history():
    try:
        engine = MetaAgentTrainerEngine()
        return {"status": "success", "history": engine.history.model_dump(mode='json')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
