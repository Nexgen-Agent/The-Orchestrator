from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from agents.system_resilience.resilience import ResilienceManager
from agents.system_resilience.models import ResilienceReport, ResilienceAction

router = APIRouter(prefix="/resilience", tags=["resilience"])
resilience = ResilienceManager()

@router.post("/analyze-and-fix", response_model=ResilienceReport)
async def analyze_and_fix():
    return await resilience.detect_and_fix()

@router.get("/history", response_model=List[ResilienceAction])
async def get_history():
    return resilience.get_resilience_history()

@router.post("/safe-mode")
async def set_safe_mode(active: bool):
    resilience.set_safe_mode(active)
    return {"status": "success", "message": f"Safe mode set to {active}"}

@router.get("/status")
async def get_status():
    from fog.core.state import state_store
    state = state_store.get_state()
    return {
        "safe_mode": state.get("safe_mode", False),
        "total_actions": len(state.get("resilience_actions", []))
    }
