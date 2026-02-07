from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from agents.learning_feedback.feedback import LearningFeedbackAgent
from agents.learning_feedback.models import FeedbackReport, LearningMemory

router = APIRouter(prefix="/learning", tags=["learning"])
agent = LearningFeedbackAgent()

@router.post("/analyze", response_model=FeedbackReport)
async def run_analysis(feed_to_evolution: bool = True):
    report = agent.analyze_performance()
    if feed_to_evolution:
        agent.feed_to_evolution_coordinator(report)
    return report

@router.post("/trigger", response_model=FeedbackReport)
async def trigger_learning():
    report = agent.analyze_performance()
    agent.feed_to_evolution_coordinator(report)
    return report

@router.get("/memory", response_model=LearningMemory)
async def get_memory():
    return agent.memory

@router.get("/proposals")
async def get_proposals():
    from fog.core.state import state_store
    state = state_store.get_state()
    return state.get("evolution_proposals", [])
