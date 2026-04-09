"""Clipboard Manager — Pin service layer."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ClipboardService:
    """Business-logic service for Pin operations in Clipboard Manager."""

    def __init__(
        self,
        repo: Any,
        events: Optional[Any] = None,
    ) -> None:
        self._repo   = repo
        self._events = events
        logger.debug("ClipboardService started")

    def paste(
        self, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the paste workflow for a new Pin."""
        if "pinned" not in payload:
            raise ValueError("Missing required field: pinned")
        record = self._repo.insert(
            payload["pinned"], payload.get("size_bytes"),
            **{k: v for k, v in payload.items()
              if k not in ("pinned", "size_bytes")}
        )
        if self._events:
            self._events.emit("pin.pasted", record)
        return record

    def clear(self, rec_id: str, **changes: Any) -> Dict[str, Any]:
        """Apply *changes* to a Pin and emit a change event."""
        ok = self._repo.update(rec_id, **changes)
        if not ok:
            raise KeyError(f"Pin {rec_id!r} not found")
        updated = self._repo.fetch(rec_id)
        if self._events:
            self._events.emit("pin.cleard", updated)
        return updated

    def copy(self, rec_id: str) -> None:
        """Remove a Pin and emit a removal event."""
        ok = self._repo.delete(rec_id)
        if not ok:
            raise KeyError(f"Pin {rec_id!r} not found")
        if self._events:
            self._events.emit("pin.copyd", {"id": rec_id})

    def search(
        self,
        pinned: Optional[Any] = None,
        status: Optional[str] = None,
        limit:  int = 50,
    ) -> List[Dict[str, Any]]:
        """Search pins by *pinned* and/or *status*."""
        filters: Dict[str, Any] = {}
        if pinned is not None:
            filters["pinned"] = pinned
        if status is not None:
            filters["status"] = status
        rows, _ = self._repo.query(filters, limit=limit)
        logger.debug("search pins: %d hits", len(rows))
        return rows

    @property
    def stats(self) -> Dict[str, int]:
        """Quick summary of Pin counts by status."""
        result: Dict[str, int] = {}
        for status in ("active", "pending", "closed"):
            _, count = self._repo.query({"status": status}, limit=0)
            result[status] = count
        return result
