import asyncio
from typing import Dict, Any
from agents.logic_summarizer.summarizer import LogicSummarizer
from agents.logic_summarizer.connector import MockLLMConnector

async def handle_task(task_packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestration handler for FOG.
    Expects 'file_path' or 'text' in payload.
    """
    payload = task_packet.get("payload", {})
    file_path = payload.get("file_path")
    text = payload.get("text")

    # In a real scenario, we'd configure the connector based on task_packet
    connector = MockLLMConnector()
    summarizer = LogicSummarizer(connector)

    try:
        if file_path:
            output = await summarizer.summarize_file(file_path)
        elif text:
            output = await summarizer.summarize_text(text)
        else:
            return {"status": "error", "message": "Missing file_path or text in payload"}

        return {
            "status": "success",
            "result": output.model_dump(mode='json')
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
