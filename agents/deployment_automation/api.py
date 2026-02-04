from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from agents.deployment_automation.automation import DeploymentAutomation
from agents.deployment_automation.models import DeploymentReport, DeploymentManifest

router = APIRouter(prefix="/deployment", tags=["deployment"])

@router.post("/deploy", response_model=DeploymentReport)
async def run_deployment(project_path: str, manifest: DeploymentManifest):
    automation = DeploymentAutomation(project_path)
    return await automation.run_deployment(manifest)

@router.post("/rollback/{deployment_id}", response_model=DeploymentReport)
async def rollback(project_path: str, deployment_id: str):
    automation = DeploymentAutomation(project_path)
    try:
        return await automation.rollback(deployment_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/reports", response_model=List[DeploymentReport])
async def get_reports():
    from fog.core.state import state_store
    state = state_store.get_state()
    deployments = state.get("deployments", {})
    return [DeploymentReport(**r) for r in deployments.values()]

@router.get("/manifest")
async def generate_manifest(project_path: str, service_name: str, image_tag: str = "latest"):
    automation = DeploymentAutomation(project_path)
    return automation.generate_manifest(service_name, image_tag)
