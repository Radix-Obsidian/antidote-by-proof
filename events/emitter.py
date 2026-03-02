"""Structured JSON event emitter for Comply/Viper integration."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from config import settings
from engine.logger import log


def emit(finding: dict, patch: str) -> str:
    """Write a structured JSON event. Returns the output filepath."""
    event_dir = settings.events.event_dir
    Path(event_dir).mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc)
    event = {
        "event": "antidote.finding",
        "timestamp": now.isoformat(),
        "file": finding["file"],
        "function": finding["function"],
        "line": finding["line"],
        "rule": finding["rule"],
        "severity": finding["severity"],
        "patch": patch,
        "status": "unresolved",
    }

    safe_name = finding["function"].replace("/", "_")
    ts = now.strftime("%Y%m%dT%H%M%S")
    filename = f"{ts}_{safe_name}.json"
    filepath = os.path.join(event_dir, filename)

    with open(filepath, "w") as f:
        json.dump(event, f, indent=2)

    log.info(f"Event emitted: {filepath}", extra={"data": {"finding": finding["function"]}})
    return filepath
