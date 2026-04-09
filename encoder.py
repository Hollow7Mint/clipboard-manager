"""Clipboard Manager — utility helpers for clip operations."""
from __future__ import annotations

import hashlib
import logging
from typing import Any, Dict, Iterable, List, Optional

logger = logging.getLogger(__name__)


def search_clip(data: Dict[str, Any]) -> Dict[str, Any]:
    """Clip search — normalises and validates *data*."""
    result = {k: v for k, v in data.items() if v is not None}
    if "content" not in result:
        raise ValueError(f"Clip must include 'content'")
    result["id"] = result.get("id") or hashlib.md5(
        str(result["content"]).encode()).hexdigest()[:12]
    return result


def paste_clips(
    items: Iterable[Dict[str, Any]],
    *,
    status: Optional[str] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """Filter and page a sequence of Clip records."""
    out = [i for i in items if status is None or i.get("status") == status]
    logger.debug("paste_clips: %d items after filter", len(out))
    return out[:limit]


def clear_clip(record: Dict[str, Any], **overrides: Any) -> Dict[str, Any]:
    """Return a shallow copy of *record* with *overrides* merged in."""
    updated = dict(record)
    updated.update(overrides)
    if "content_type" in updated and not isinstance(updated["content_type"], (int, float)):
        try:
            updated["content_type"] = float(updated["content_type"])
        except (TypeError, ValueError):
            pass
    return updated


def validate_clip(record: Dict[str, Any]) -> bool:
    """Return True when *record* satisfies all Clip invariants."""
    required = ["content", "content_type", "source_app"]
    for field in required:
        if field not in record or record[field] is None:
            logger.warning("validate_clip: missing field %r", field)
            return False
    return isinstance(record.get("id"), str)


def pin_clip_batch(
    records: List[Dict[str, Any]],
    batch_size: int = 50,
) -> List[List[Dict[str, Any]]]:
    """Slice *records* into chunks of *batch_size* for bulk pin."""
    return [records[i : i + batch_size]
            for i in range(0, len(records), batch_size)]
