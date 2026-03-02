"""Pydantic schemas for the Antidote REST API."""

from pydantic import BaseModel, Field


class ScanRequest(BaseModel):
    target: str = Field(..., description="File or directory path to scan")


class FindingResponse(BaseModel):
    file: str
    function: str
    line: int
    rule: str
    severity: str


class ScanResponse(BaseModel):
    scan_id: str
    status: str
    target: str
    started_at: str
    finished_at: str
    files_scanned: int
    total_findings: int
    findings: list[FindingResponse]
    events: list[str]
    errors: list[dict]


class HealthResponse(BaseModel):
    status: str
    version: str
    scanner: str
    ai: dict


class AIStatusResponse(BaseModel):
    status: str
    backend_config: str
    mlx: dict
    ollama: dict
    metrics: dict
