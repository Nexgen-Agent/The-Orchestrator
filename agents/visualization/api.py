from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from typing import List, Dict, Any, Optional
import os
from agents.visualization.visualizer import VisualizationAgent
from agents.visualization.models import VisualizationRequest, VisualizationOutput

router = APIRouter(prefix="/visualization", tags=["visualization"])
agent = VisualizationAgent()

@router.post("/generate", response_model=VisualizationOutput)
async def generate_visualization(request: VisualizationRequest):
    try:
        return agent.generate_visualization(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/list", response_model=List[str])
async def list_visualizations():
    return agent.list_visualizations()

@router.get("/download/{filename}")
async def download_visualization(filename: str):
    path = os.path.join(agent.output_dir, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path)
