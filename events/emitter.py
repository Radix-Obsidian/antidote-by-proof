"""Structured JSON event emitter for Comply/Viper integration."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_EVENT_DIR = os.environ.get("ANTIDOTE_EVENT_DIR", "./events/antidote")


def emit(finding: dict, patch: str, event_dir: str = DEFAULT_EVENT_DIR) -> str:
    """Write a structured JSON event. Returns the output filepath."""
    Path(event_dir).mkdir(parents=True, exist_ok=True)

    event = {
        "event": "antidote.finding",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "file": finding["file"],
        "function": finding["function"],
        "line": finding["line"],
        "rule": finding["rule"],
        "severity": finding["severity"],
        "patch": patch,
        "status": "unresolved",
    }

    safe_name = finding["function"].replace("/", "_")
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    filename = f"{ts}_{safe_name}.json"
    filepath = os.path.join(event_dir, filename)

    with open(filepath, "w") as f:
        json.dump(event, f, indent=2)

    return filepath
