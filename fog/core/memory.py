from typing import List, Dict, Any
from datetime import datetime
import json
import os

class ConversationManager:
    """
    Manages the conversation state and history for the Orchestrator.
    """
    def __init__(self, storage_path: str = "storage/chat_history.json"):
        self.storage_path = storage_path
        self.sessions: Dict[str, List[Dict[str, Any]]] = {}
        self._load_history()

    def _load_history(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    self.sessions = json.load(f)
            except Exception:
                self.sessions = {}

    def _save_history(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, "w") as f:
            json.dump(self.sessions, f, indent=4)

    def add_message(self, session_id: str, role: str, content: str, metadata: Dict[str, Any] = None):
        if session_id not in self.sessions:
            self.sessions[session_id] = []

        self.sessions[session_id].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        })

        # Keep only last 20 messages for context
        if len(self.sessions[session_id]) > 20:
            self.sessions[session_id] = self.sessions[session_id][-20:]

        self._save_history()

    def get_context(self, session_id: str) -> List[Dict[str, Any]]:
        return self.sessions.get(session_id, [])

    def clear_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]
            self._save_history()

# Global instance
conversation_manager = ConversationManager()
