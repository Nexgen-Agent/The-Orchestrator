import asyncio
from typing import Dict, Any
from agents.knowledge_memory.memory_store import MemoryStore

async def handle_task(task_packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestration handler for FOG.
    Supported actions in payload: 'store', 'search', 'list'.
    """
    payload = task_packet.get("payload", {})
    action = payload.get("action", "search")

    # In a real system, the storage path might be configurable via task_packet or env
    store = MemoryStore()

    try:
        if action == "store":
            title = payload.get("title")
            problem = payload.get("problem")
            solution = payload.get("solution")
            tags = payload.get("tags", [])
            metadata = payload.get("metadata", {})

            if not all([title, problem, solution]):
                return {"status": "error", "message": "Missing required fields for store action: title, problem, solution"}

            # Using asyncio.to_thread for blocking I/O (file save)
            result = await asyncio.to_thread(store.add_entry, title, problem, solution, tags, metadata)
            return {
                "status": "success",
                "result": result.model_dump(mode='json')
            }

        elif action == "search":
            query = payload.get("query")
            tags = payload.get("tags")
            limit = payload.get("limit", 10)

            # Using asyncio.to_thread for consistency
            result = await asyncio.to_thread(store.search, query, tags, limit)
            return {
                "status": "success",
                "result": result.model_dump(mode='json')
            }

        elif action == "list":
            # Using asyncio.to_thread
            entries = await asyncio.to_thread(store.get_all)
            return {
                "status": "success",
                "result": {"entries": [e.model_dump(mode='json') for e in entries]}
            }

        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
