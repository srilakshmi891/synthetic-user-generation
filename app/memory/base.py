from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BasePersonaMemory(ABC):
    """
    Abstract Base Class defining the contract for Persona Memory storage.
    Supports isolated per-persona per-session multi-turn conversation storage.
    """

    @abstractmethod
    def add_turn(
        self,
        persona_id: str,
        session_id: str,
        user_query: str,
        persona_response: str
    ) -> None:
        """
        Appends a conversation turn to the memory of a specific persona and session.
        """
        pass

    @abstractmethod
    def get_history(
        self,
        persona_id: str,
        session_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieves recent N conversation turns for a given persona and session.
        Returns a list of dicts with keys: 'role' ('user'/'assistant'), 'content', 'timestamp'.
        """
        pass

    @abstractmethod
    def clear_memory(
        self,
        persona_id: str,
        session_id: str
    ) -> bool:
        """
        Clears/resets the conversation memory for a given persona and session.
        """
        pass
