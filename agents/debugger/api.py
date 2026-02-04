from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from agents.debugger.debugger import Debugger
from agents.debugger.models import DebugRequest, DebugReport

router = APIRouter(prefix="/debugger", tags=["debugger"])

@router.post("/run", response_model=DebugReport)
async def run_debug(request: DebugRequest):
    debugger = Debugger(request.project_path)
    try:
        return await debugger.run_debug(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_debug_history():
    from fog.core.state import state_store
    return state_store.get_state().get("debug_history", [])
