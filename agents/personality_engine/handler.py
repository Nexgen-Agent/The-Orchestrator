import asyncio
from typing import Dict, Any
from agents.personality_engine.analyzer import InteractionAnalyzer
from agents.personality_engine.engine import FingerprintManager, StyleAdaptor

async def handle_task(task_packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestration handler for FOG.
    Supports:
    - 'LEARN_STYLE': Analyzes text and updates user fingerprint.
    - 'GET_PERSONALITY_PARAMS': Returns adaptation parameters for a user.
    """
    payload = task_packet.get("payload", {})
    task_type = payload.get("task_type", "LEARN_STYLE")
    user_id = payload.get("user_id", "default_user")

    manager = FingerprintManager()
    analyzer = InteractionAnalyzer()

    try:
        if task_type == "LEARN_STYLE":
            text = payload.get("text")
            if not text:
                return {"status": "error", "message": "Missing 'text' in payload"}

            analysis = analyzer.analyze_text(text)
            manager.update_profile(user_id, analysis)

            return {
                "status": "success",
                "result": {
                    "analysis": analysis.model_dump(mode='json'),
                    "profile": manager.get_profile(user_id).model_dump(mode='json')
                }
            }

        elif task_type == "GET_PERSONALITY_PARAMS":
            profile = manager.get_profile(user_id)
            params = StyleAdaptor.generate_adaptation(profile)

            return {
                "status": "success",
                "result": params.model_dump(mode='json')
            }

        else:
            return {"status": "error", "message": f"Unknown task_type: {task_type}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
