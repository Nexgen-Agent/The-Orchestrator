import asyncio
from typing import Dict, Any
from agents.website_insight_scout.scout import WebsiteScout
from agents.website_insight_scout.connector import MockAIInsightConnector

async def handle_task(task_packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestration handler for FOG.
    Expects 'url' in payload.
    Optional: 'analyze_ui', 'analyze_ux'
    """
    payload = task_packet.get("payload", {})
    url = payload.get("url")
    analyze_ui = payload.get("analyze_ui", True)
    analyze_ux = payload.get("analyze_ux", True)

    if not url:
        return {"status": "error", "message": "Missing 'url' in payload"}

    # Configure connector (mock for now)
    connector = MockAIInsightConnector()
    scout = WebsiteScout(connector)

    try:
        analysis = await scout.analyze(url, analyze_ui=analyze_ui, analyze_ux=analyze_ux)
        return {
            "status": "success",
            "result": analysis.model_dump(mode='json')
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
