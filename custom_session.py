from agents.memory.session import SessionABC
from agents.items import TResponseInputItem
from typing import List, Any
import json
import os
import dataclasses

class CustomSession(SessionABC):
    """Custom session implementation following the Session protocol."""

    def __init__(self, session_id: str, title: str | None = None, description: str | None = None):
        self.session_id = session_id
        self.title = title
        self.description = description
        # Load existing session file if present so we don't require title/description on subsequent constructions
        path = self._session_filepath()
        if os.path.exists(path):
            data = self._read_session_file()
            # Use stored metadata if not provided
            if self.title is None:
                self.title = data.get("title", "")
            if self.description is None:
                self.description = data.get("description", "")
            self.conversation = data.get("conversation", [])
        else:
            # Defaults for a new session
            self.title = self.title or ""
            self.description = self.description or ""
            self.conversation = []

    def _session_filepath(self) -> str:
        base_dir = os.path.dirname(__file__)
        sessions_dir = os.path.join(base_dir, "conversations")
        os.makedirs(sessions_dir, exist_ok=True)
        return os.path.join(sessions_dir, f"{self.session_id}.json")

    def _serialize_item(self, item: Any) -> Any:
        # Try common conversions so the item is JSON serializable
        if isinstance(item, dict):
            return item
        if dataclasses.is_dataclass(item):
            return dataclasses.asdict(item)
        if hasattr(item, "dict") and callable(getattr(item, "dict")):
            return item.dict()
        try:
            return vars(item)
        except Exception:
            return item  # fallback; json may still fail if not serializable

    def _read_session_file(self) -> dict:
        path = self._session_filepath()
        if not os.path.exists(path):
            return {"session_id": self.session_id, "title": self.title, "description": self.description, "conversation": []}
        with open(path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {"session_id": self.session_id, "title": self.title, "description": self.description, "conversation": []}
        # ensure keys exist
        data.setdefault("session_id", self.session_id)
        data.setdefault("title", self.title)
        data.setdefault("description", self.description)
        data.setdefault("conversation", [])
        return data

    def _write_session_file(self, data: dict) -> None:
        path = self._session_filepath()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    async def get_items(self, limit: int | None = None) -> List[TResponseInputItem]:
        """Retrieve conversation history for this session."""
        data = self._read_session_file()
        conv = data.get("conversation", [])
        if limit is not None:
            conv = conv[-limit:]
        return conv

    async def add_items(self, items: List[TResponseInputItem]) -> None:
        """Store new items for this session."""
        data = self._read_session_file()
        existing = data.get("conversation", [])
        # serialize each incoming item to a JSON-friendly form
        serialized = [self._serialize_item(it) for it in items]
        data["conversation"] = existing + serialized
        # ensure metadata is up-to-date
        data["session_id"] = self.session_id
        data["title"] = self.title
        data["description"] = self.description
        self._write_session_file(data)

    async def pop_item(self) -> TResponseInputItem | None:
        """Remove and return the most recent item from this session."""
        data = self._read_session_file()
        conv = data.get("conversation", [])
        if not conv:
            return None
        item = conv.pop()  # most recent (last) item
        data["conversation"] = conv
        self._write_session_file(data)
        return item

    async def clear_session(self) -> None:
        """Clear all items for this session."""
        data = {"session_id": self.session_id, "title": self.title, "description": self.description, "conversation": []}
        self._write_session_file(data) 