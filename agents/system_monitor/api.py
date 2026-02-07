from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from agents.system_monitor.monitor import SystemMonitor
from agents.system_monitor.models import SystemHealthReport
from fog.core.state import state_store

router = APIRouter(prefix="/system-monitor", tags=["system-monitor"])

@router.get("/health", response_model=SystemHealthReport)
async def get_health():
    monitor = SystemMonitor(state_store)
    try:
        return monitor.get_health_report()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
