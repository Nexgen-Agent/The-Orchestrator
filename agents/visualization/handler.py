import asyncio
from typing import Dict, Any
from agents.visualization.visualizer import VisualizationAgent
from agents.visualization.models import VisualizationRequest, GraphType

async def handle_task(task_packet_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestration handler for Visualization Agent.
    """
    payload = task_packet_dict.get("payload", {})
    graph_type_str = payload.get("graph_type")
    data = payload.get("data")

    if not graph_type_str or not data:
        return {"status": "error", "message": "Missing 'graph_type' or 'data' in payload"}

    try:
        graph_type = GraphType(graph_type_str)
        request = VisualizationRequest(
            graph_type=graph_type,
            data=data,
            output_format=payload.get("output_format", "png"),
            title=payload.get("title")
        )

        agent = VisualizationAgent()
        # Running in to_thread because matplotlib/networkx are CPU intensive
        output = await asyncio.to_thread(agent.generate_visualization, request)

        return {
            "status": "success",
            "result": output.model_dump(mode='json')
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
