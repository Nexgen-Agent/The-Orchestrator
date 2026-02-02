import json
import os
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from agents.knowledge_memory.models import KnowledgeEntry, SearchResult, MemoryOperationResult

class MemoryStore:
    def __init__(self, storage_path: str = "storage/knowledge_memory.json"):
        self.storage_path = storage_path
        self._ensure_storage_exists()
        self.entries: List[KnowledgeEntry] = self._load_entries()

    def _ensure_storage_exists(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, "w") as f:
                json.dump([], f)

    def _load_entries(self) -> List[KnowledgeEntry]:
        try:
            with open(self.storage_path, "r") as f:
                data = json.load(f)
                return [KnowledgeEntry(**entry) for entry in data]
        except (json.JSONDecodeError, Exception):
            return []

    def _save_entries(self):
        with open(self.storage_path, "w") as f:
            data = [entry.model_dump(mode='json') for entry in self.entries]
            json.dump(data, f, indent=2, default=str)

    def add_entry(self, title: str, problem: str, solution: str, tags: List[str] = None, metadata: Dict[str, Any] = None) -> MemoryOperationResult:
        entry_id = str(uuid.uuid4())
        new_entry = KnowledgeEntry(
            id=entry_id,
            title=title,
            problem=problem,
            solution=solution,
            tags=tags or [],
            metadata=metadata or {},
            timestamp=datetime.now(timezone.utc)
        )
        self.entries.append(new_entry)
        self._save_entries()
        return MemoryOperationResult(success=True, message="Entry added successfully", entry_id=entry_id)

    def search(self, query: Optional[str] = None, tags: Optional[List[str]] = None, limit: int = 10) -> SearchResult:
        filtered = self.entries

        if tags:
            filtered = [e for e in filtered if all(tag in e.tags for tag in tags)]

        if query:
            query = query.lower()
            filtered = [
                e for e in filtered
                if query in e.title.lower() or query in e.problem.lower() or query in e.solution.lower()
            ]

        # Sort by timestamp descending
        filtered.sort(key=lambda x: x.timestamp, reverse=True)

        results = filtered[:limit]
        return SearchResult(entries=results, count=len(results), query=query, tags=tags)

    def get_all(self) -> List[KnowledgeEntry]:
        return self.entries
