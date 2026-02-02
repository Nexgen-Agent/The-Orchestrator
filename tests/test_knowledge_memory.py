import pytest
import os
import json
from agents.knowledge_memory.memory_store import MemoryStore
from agents.knowledge_memory.handler import handle_task

@pytest.fixture
def temp_storage(tmp_path):
    storage_file = tmp_path / "test_knowledge.json"
    return str(storage_file)

def test_store_and_search(temp_storage):
    store = MemoryStore(storage_path=temp_storage)

    # Test Add
    res = store.add_entry(
        title="Test Title",
        problem="Test Problem",
        solution="Test Solution",
        tags=["test", "unit"]
    )
    assert res.success is True
    assert res.entry_id is not None

    # Test Search by Query
    search_res = store.search(query="Solution")
    assert search_res.count == 1
    assert search_res.entries[0].title == "Test Title"

    # Test Search by Tag
    search_res = store.search(tags=["unit"])
    assert search_res.count == 1

    # Test Search No Match
    search_res = store.search(query="Missing")
    assert search_res.count == 0

@pytest.mark.asyncio
async def test_handler_store_and_search(temp_storage, monkeypatch):
    from agents.knowledge_memory import handler

    # Patch MemoryStore to use temp_storage
    monkeypatch.setattr(handler, "MemoryStore", lambda: MemoryStore(storage_path=temp_storage))

    # Test Handler Store
    task = {
        "payload": {
            "action": "store",
            "title": "Handler Title",
            "problem": "Handler Problem",
            "solution": "Handler Solution",
            "tags": ["handler"]
        }
    }
    response = await handle_task(task)
    assert response["status"] == "success"
    assert response["result"]["success"] is True

    # Test Handler Search
    search_task = {
        "payload": {
            "action": "search",
            "query": "Handler"
        }
    }
    search_response = await handle_task(search_task)
    assert search_response["status"] == "success"
    assert search_response["result"]["count"] == 1
    assert search_response["result"]["entries"][0]["title"] == "Handler Title"
