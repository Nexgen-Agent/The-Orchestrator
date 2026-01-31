import json
import os
from typing import Any, Dict, List, Optional
from threading import Lock

class StateStore:
    def __init__(self, storage_path: str = "storage/state.json"):
        self.storage_path = storage_path
        self.lock = Lock()
        self._state = {
            "tasks": {},
            "agents": {},
            "backups": [],
            "runs": []
        }
        self._load()

    def _load(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    self._state.update(json.load(f))
            except Exception:
                # Fallback to empty state if file is corrupt
                pass

    def _save(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, 'w') as f:
            json.dump(self._state, f, indent=4)

    def update_task(self, task_id: str, task_data: Dict[str, Any]):
        with self.lock:
            self._state["tasks"][task_id] = task_data
            self._save()

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        return self._state["tasks"].get(task_id)

    def add_agent(self, agent_name: str, agent_config: Dict[str, Any]):
        with self.lock:
            self._state["agents"][agent_name] = agent_config
            self._save()

    def get_agents(self) -> Dict[str, Any]:
        return self._state["agents"]

    def add_backup(self, backup_metadata: Dict[str, Any]):
        with self.lock:
            self._state["backups"].append(backup_metadata)
            self._save()

    def get_backups(self) -> List[Dict[str, Any]]:
        return self._state["backups"]

    def get_state(self) -> Dict[str, Any]:
        return self._state

# Global state instance
state_store = StateStore()
