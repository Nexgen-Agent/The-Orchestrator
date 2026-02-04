from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from agents.software_builder.builder import SoftwareBuilder
from agents.software_builder.models import BuildRequest, BuildReport

router = APIRouter(prefix="/builder", tags=["builder"])

@router.post("/build", response_model=BuildReport)
async def run_build(request: BuildRequest):
    builder = SoftwareBuilder(request.project_path)
    try:
        return await builder.run_build(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_build_history():
    from fog.core.state import state_store
    return state_store.get_state().get("build_history", [])
