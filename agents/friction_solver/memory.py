import json
import os
from typing import Dict, List, Optional, Any

class FrictionMemory:
    def __init__(self, memory_path: str = "storage/friction_memory.json"):
        self.memory_path = memory_path
        self._memory = {}
        self._load()

    def _load(self):
        if os.path.exists(self.memory_path):
            try:
                with open(self.memory_path, "r") as f:
                    self._memory = json.load(f)
            except Exception:
                self._memory = {}

    def _save(self):
        os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
        with open(self.memory_path, "w") as f:
            json.dump(self._memory, f, indent=4)

    def get_fix(self, error_type: str, root_cause: str) -> Optional[str]:
        # Simple lookup: check if we have a fix for this error type and root cause
        fixes = self._memory.get(error_type, {})
        return fixes.get(root_cause)

    def save_fix(self, error_type: str, root_cause: str, fix_method: str):
        if error_type not in self._memory:
            self._memory[error_type] = {}
        self._memory[error_type][root_cause] = fix_method
        self._save()
