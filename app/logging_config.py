"""Structured audit logging for inputs, intents, and proposed commands."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from app.config import settings


def _ensure_log_dir() -> Path:
    settings.log_dir.mkdir(parents=True, exist_ok=True)
    return settings.log_dir


def get_audit_logger() -> logging.Logger:
    """File + console logger for debugging and dataset improvement."""
    log = logging.getLogger("nca.audit")
    if log.handlers:
        return log
    log.setLevel(logging.INFO)
    path = _ensure_log_dir() / settings.log_file
    fh = logging.FileHandler(path, encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(message)s"))
    log.addHandler(fh)
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    ch.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
    log.addHandler(ch)
    return log


def log_interaction(payload: Dict[str, Any]) -> None:
    """Append one JSON line with timestamp (UTC)."""
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        **payload,
    }
    get_audit_logger().info(json.dumps(record, ensure_ascii=False))
