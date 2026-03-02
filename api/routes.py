"""FastAPI REST API routes for Antidote."""

import json
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException

from api.models import (
    AIStatusResponse,
    HealthResponse,
    ScanRequest,
    ScanResponse,
)
from config import settings
from engine.ai_core import health_check as ai_health_check
from engine.scanner import run_scan

router = APIRouter()

VERSION = "1.0.0"


@router.get("/health", response_model=HealthResponse)
def health():
    ai = ai_health_check()
    return HealthResponse(
        status="healthy" if ai["status"] == "healthy" else "degraded",
        version=VERSION,
        scanner="tree-sitter",
        ai=ai,
    )


@router.post("/scan", response_model=ScanResponse)
def scan(req: ScanRequest):
    target = req.target
    if not os.path.exists(target):
        raise HTTPException(status_code=404, detail=f"Path not found: {target}")

    result = run_scan(target)

    findings = []
    for f in result.findings:
        findings.append({
            "file": f["file"],
            "function": f["function"],
            "line": f["line"],
            "rule": f["rule"],
            "severity": f["severity"],
        })

    return ScanResponse(
        scan_id=result.scan_id,
        status=result.status,
        target=result.target,
        started_at=result.started_at,
        finished_at=result.finished_at,
        files_scanned=result.files_scanned,
        total_findings=result.total_findings,
        findings=findings,
        events=result.events,
        errors=result.errors,
    )


@router.get("/ai/status", response_model=AIStatusResponse)
def ai_status():
    status = ai_health_check()
    return AIStatusResponse(**status)


@router.get("/findings")
def list_findings():
    """List all emitted finding events from the event directory."""
    event_dir = Path(settings.events.event_dir)
    if not event_dir.exists():
        return {"findings": [], "total": 0}

    findings = []
    for fpath in sorted(event_dir.glob("*.json"), reverse=True):
        try:
            with open(fpath) as f:
                data = json.load(f)
            data["_event_file"] = fpath.name
            findings.append(data)
        except Exception:
            continue

    return {"findings": findings, "total": len(findings)}


@router.get("/findings/{filename}")
def get_finding(filename: str):
    """Get a specific finding event by filename."""
    fpath = Path(settings.events.event_dir) / filename
    if not fpath.exists():
        raise HTTPException(status_code=404, detail="Finding not found")
    with open(fpath) as f:
        return json.load(f)
