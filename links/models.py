"""Clipboard Manager — Tag service layer."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ClipboardModels:
    """Business-logic service for Tag operations in Clipboard Manager."""

    def __init__(
        self,
        repo: Any,
        events: Optional[Any] = None,
    ) -> None:
        self._repo   = repo
        self._events = events
        logger.debug("ClipboardModels started")

    def paste(
        self, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the paste workflow for a new Tag."""
        if "content" not in payload:
            raise ValueError("Missing required field: content")
        record = self._repo.insert(
            payload["content"], payload.get("created_at"),
            **{k: v for k, v in payload.items()
              if k not in ("content", "created_at")}
        )
        if self._events:
            self._events.emit("tag.pasted", record)
        return record

    def sync(self, rec_id: str, **changes: Any) -> Dict[str, Any]:
        """Apply *changes* to a Tag and emit a change event."""
        ok = self._repo.update(rec_id, **changes)
        if not ok:
            raise KeyError(f"Tag {rec_id!r} not found")
        updated = self._repo.fetch(rec_id)
        if self._events:
            self._events.emit("tag.syncd", updated)
        return updated

    def copy(self, rec_id: str) -> None:
        """Remove a Tag and emit a removal event."""
        ok = self._repo.delete(rec_id)
        if not ok:
            raise KeyError(f"Tag {rec_id!r} not found")
        if self._events:
            self._events.emit("tag.copyd", {"id": rec_id})

    def search(
        self,
        content: Optional[Any] = None,
        status: Optional[str] = None,
        limit:  int = 50,
    ) -> List[Dict[str, Any]]:
        """Search tags by *content* and/or *status*."""
        filters: Dict[str, Any] = {}
        if content is not None:
            filters["content"] = content
        if status is not None:
            filters["status"] = status
        rows, _ = self._repo.query(filters, limit=limit)
        logger.debug("search tags: %d hits", len(rows))
        return rows

    @property
    def stats(self) -> Dict[str, int]:
        """Quick summary of Tag counts by status."""
        result: Dict[str, int] = {}
        for status in ("active", "pending", "closed"):
            _, count = self._repo.query({"status": status}, limit=0)
            result[status] = count
        return result
