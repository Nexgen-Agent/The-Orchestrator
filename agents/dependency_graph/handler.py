import asyncio
from typing import Dict, Any
from agents.dependency_graph.graph import DependencyGraphAgent

async def handle_task(task_packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestration handler for FOG.
    Expects 'analyzer_output' in payload.
    """
    payload = task_packet.get("payload", {})
    analyzer_output = payload.get("analyzer_output")

    if not analyzer_output:
        return {"status": "error", "message": "Missing analyzer_output in payload"}

    try:
        agent = DependencyGraphAgent()
        # analyzer_output could be a JSON string or a dict
        if isinstance(analyzer_output, str):
            import json
            analyzer_output = json.loads(analyzer_output)

        agent.build_graph(analyzer_output)
        analysis = agent.analyze()

        return {
            "status": "success",
            "result": analysis.model_dump(mode='json')
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
