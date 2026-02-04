from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List
from agents.shooting_star_ingestion.ingestion import ShootingStarIngestion
from agents.shooting_star_ingestion.models import IngestionReport
from fog.core.state import state_store

router = APIRouter(prefix="/ingestion", tags=["ingestion"])

@router.post("/start", response_model=IngestionReport)
async def start_ingestion(project_path: str, background_tasks: BackgroundTasks):
    ingestion = ShootingStarIngestion(project_path)
    # We could run this in background, but for simplicity of returning the report:
    report = await ingestion.ingest()

    # Store in state
    state = state_store.get_state()
    if "ingestions" not in state:
        state["ingestions"] = {}
    state["ingestions"][report.ingestion_id] = report.model_dump(mode='json')
    state_store._save()

    return report

@router.get("/reports", response_model=List[IngestionReport])
async def get_reports():
    state = state_store.get_state()
    ingestions = state.get("ingestions", {})
    return [IngestionReport(**r) for r in ingestions.values()]

@router.get("/report/{ingestion_id}", response_model=IngestionReport)
async def get_report(ingestion_id: str):
    state = state_store.get_state()
    report_data = state.get("ingestions", {}).get(ingestion_id)
    if not report_data:
        raise HTTPException(status_code=404, detail="Ingestion report not found")
    return IngestionReport(**report_data)
