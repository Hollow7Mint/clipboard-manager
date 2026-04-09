"""Clipboard Manager — utility helpers for pin operations."""
from __future__ import annotations

import hashlib
import logging
from typing import Any, Dict, Iterable, List, Optional

logger = logging.getLogger(__name__)


def paste_pin(data: Dict[str, Any]) -> Dict[str, Any]:
    """Pin paste — normalises and validates *data*."""
    result = {k: v for k, v in data.items() if v is not None}
    if "size_bytes" not in result:
        raise ValueError(f"Pin must include 'size_bytes'")
    result["id"] = result.get("id") or hashlib.md5(
        str(result["size_bytes"]).encode()).hexdigest()[:12]
    return result


def copy_pins(
    items: Iterable[Dict[str, Any]],
    *,
    status: Optional[str] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """Filter and page a sequence of Pin records."""
    out = [i for i in items if status is None or i.get("status") == status]
    logger.debug("copy_pins: %d items after filter", len(out))
    return out[:limit]


def clear_pin(record: Dict[str, Any], **overrides: Any) -> Dict[str, Any]:
    """Return a shallow copy of *record* with *overrides* merged in."""
    updated = dict(record)
    updated.update(overrides)
    if "pinned" in updated and not isinstance(updated["pinned"], (int, float)):
        try:
            updated["pinned"] = float(updated["pinned"])
        except (TypeError, ValueError):
            pass
    return updated


def validate_pin(record: Dict[str, Any]) -> bool:
    """Return True when *record* satisfies all Pin invariants."""
    required = ["size_bytes", "pinned", "created_at"]
    for field in required:
        if field not in record or record[field] is None:
            logger.warning("validate_pin: missing field %r", field)
            return False
    return isinstance(record.get("id"), str)


def sync_pin_batch(
    records: List[Dict[str, Any]],
    batch_size: int = 50,
) -> List[List[Dict[str, Any]]]:
    """Slice *records* into chunks of *batch_size* for bulk sync."""
    return [records[i : i + batch_size]
            for i in range(0, len(records), batch_size)]
