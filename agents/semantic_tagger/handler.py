import asyncio
from typing import Dict, Any
from agents.semantic_tagger.tagger import SemanticTagger
from agents.semantic_tagger.connector import MockAIModelConnector

async def handle_task(task_packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestration handler for FOG.
    Expects 'file_path' or 'text' in payload.
    """
    payload = task_packet.get("payload", {})
    file_path = payload.get("file_path")
    text = payload.get("text")

    # Configure connector (mock for now)
    connector = MockAIModelConnector()
    tagger = SemanticTagger(connector)

    try:
        if file_path:
            analysis = await tagger.tag_file(file_path)
        elif text:
            analysis = await tagger.tag_text(text)
        else:
            return {"status": "error", "message": "Missing file_path or text in payload"}

        return {
            "status": "success",
            "result": analysis.model_dump(mode='json')
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
