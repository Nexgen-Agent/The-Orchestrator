import asyncio
from typing import Dict, Any
from agents.website_insight_scout.scout import WebsiteScout
from agents.website_insight_scout.multi_scout import MultiWebsiteScout
from agents.website_insight_scout.connector import MockAIInsightConnector
from agents.website_insight_scout.scoring import compare_sites
from agents.website_insight_scout.replication import generate_replication_manifest

async def handle_task(task_packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestration handler for FOG.
    Supports:
    - 'analyze': Single URL analysis.
    - 'multi_analyze': Multiple URL analysis and comparison.
    - 'generate_replication': Generate manifest for replication.
    """
    payload = task_packet.get("payload", {})
    task_type = payload.get("task_type", "analyze")

    # Configure connector (mock for now)
    connector = MockAIInsightConnector()
    scout = WebsiteScout(connector)

    try:
        if task_type == "analyze":
            url = payload.get("url")
            if not url:
                return {"status": "error", "message": "Missing 'url' in payload"}
            analysis = await scout.analyze(url)
            return {
                "status": "success",
                "result": analysis.model_dump(mode='json')
            }

        elif task_type == "multi_analyze":
            urls = payload.get("urls", [])
            if not urls:
                return {"status": "error", "message": "Missing 'urls' in payload"}

            multi_scout = MultiWebsiteScout(scout)
            results = await multi_scout.analyze_batch(urls)
            comparison = compare_sites(results)

            return {
                "status": "success",
                "result": {
                    "comparison": comparison.model_dump(mode='json'),
                    "individual_results": [r.model_dump(mode='json') for r in results]
                }
            }

        elif task_type == "generate_replication":
            url = payload.get("url")
            if not url:
                return {"status": "error", "message": "Missing 'url' in payload"}

            analysis = await scout.analyze(url)
            manifest = generate_replication_manifest(analysis)

            return {
                "status": "success",
                "result": manifest.model_dump(mode='json')
            }

        else:
            return {"status": "error", "message": f"Unknown task_type: {task_type}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
