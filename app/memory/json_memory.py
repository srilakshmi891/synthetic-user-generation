import os
import json
import datetime
import threading
from typing import List, Dict, Any
from app.memory.base import BasePersonaMemory

class JSONPersonaMemory(BasePersonaMemory):
    """
    File-based JSON implementation of BasePersonaMemory.
    Persists isolated persona conversation history to disk.
    Ensures safe thread-safe operations and automatic directory creation.
    """

    def __init__(self, storage_dir: str = "data/memory"):
        self.storage_dir = storage_dir
        self._lock = threading.Lock()
        os.makedirs(self.storage_dir, exist_ok=True)

    def _get_file_path(self, persona_id: str, session_id: str) -> str:
        # Sanitize identifiers to prevent directory traversal
        safe_persona_id = "".join(c for c in persona_id if c.isalnum() or c in ("-", "_")).lower()
        safe_session_id = "".join(c for c in session_id if c.isalnum() or c in ("-", "_")).lower()
        if not safe_persona_id:
            safe_persona_id = "default_persona"
        if not safe_session_id:
            safe_session_id = "default_session"
        return os.path.join(self.storage_dir, f"{safe_persona_id}_{safe_session_id}.json")

    def _read_data(self, file_path: str) -> List[Dict[str, Any]]:
        if not os.path.exists(file_path):
            return []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[JSONPersonaMemory] Error reading memory file {file_path}: {e}")
            return []

    def _write_data(self, file_path: str, data: List[Dict[str, Any]]) -> None:
        try:
            tmp_path = f"{file_path}.tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(tmp_path, file_path)
        except Exception as e:
            print(f"[JSONPersonaMemory] Error writing memory file {file_path}: {e}")

    def add_turn(
        self,
        persona_id: str,
        session_id: str,
        user_query: str,
        persona_response: str
    ) -> None:
        file_path = self._get_file_path(persona_id, session_id)
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()

        user_msg = {
            "role": "user",
            "content": user_query,
            "timestamp": now_str
        }
        assistant_msg = {
            "role": "assistant",
            "content": persona_response,
            "timestamp": now_str
        }

        with self._lock:
            history = self._read_data(file_path)
            history.append(user_msg)
            history.append(assistant_msg)
            self._write_data(file_path, history)

    def get_history(
        self,
        persona_id: str,
        session_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        file_path = self._get_file_path(persona_id, session_id)
        with self._lock:
            history = self._read_data(file_path)
            if limit > 0:
                # Return last `limit` messages (turns)
                return history[-limit * 2 :] if len(history) > limit * 2 else history
            return history

    def clear_memory(
        self,
        persona_id: str,
        session_id: str
    ) -> bool:
        file_path = self._get_file_path(persona_id, session_id)
        with self._lock:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    return True
                except Exception as e:
                    print(f"[JSONPersonaMemory] Error removing memory file {file_path}: {e}")
                    return False
            return True


# Global default memory instance
memory_service = JSONPersonaMemory()
