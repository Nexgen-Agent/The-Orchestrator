from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from agents.meta_evolution.analyzer import MetaEvolutionAnalyzer
from agents.meta_evolution.models import EvolutionStrategy, EcosystemSnapshot, TrendAnalysis

router = APIRouter(prefix="/meta-evolution", tags=["meta-evolution"])
analyzer = MetaEvolutionAnalyzer()

@router.post("/analyze", response_model=EvolutionStrategy)
async def analyze_ecosystem():
    return analyzer.propose_evolution()

@router.post("/snapshot", response_model=EcosystemSnapshot)
async def take_snapshot():
    return analyzer.take_snapshot()

@router.get("/trends", response_model=List[TrendAnalysis])
async def get_trends():
    return analyzer.analyze_trends()

@router.get("/snapshots", response_model=List[EcosystemSnapshot])
async def get_snapshots():
    from fog.core.state import state_store
    state = state_store.get_state()
    return [EcosystemSnapshot(**s) for s in state.get("ecosystem_snapshots", [])]
