"""Batch scanner — scans directories with parallel processing and progress tracking."""

import os
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from config import settings
from engine.ast_parser import scan_file
from engine.logger import log
from engine.patch_generator import generate_patch
from events.emitter import emit


@dataclass
class ScanResult:
    scan_id: str
    started_at: str
    finished_at: str = ""
    target: str = ""
    files_scanned: int = 0
    files_skipped: int = 0
    total_findings: int = 0
    findings: list = field(default_factory=list)
    events: list = field(default_factory=list)
    status: str = "running"
    errors: list = field(default_factory=list)


def _collect_files(target: str) -> list[str]:
    """Collect all scannable Python files from a target path."""
    target_path = Path(target)
    if target_path.is_file():
        return [str(target_path)]

    files = []
    exclude_dirs = set(settings.scan.exclude_dirs)
    exclude_files = set(settings.scan.exclude_files)
    max_size = settings.scan.max_file_size_kb * 1024

    for root, dirs, filenames in os.walk(target_path):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for fname in filenames:
            if fname in exclude_files:
                continue
            if not any(fname.endswith(ext) for ext in settings.scan.extensions):
                continue
            fpath = os.path.join(root, fname)
            if os.path.getsize(fpath) > max_size:
                continue
            files.append(fpath)

    return files


def _process_file(filepath: str) -> dict:
    """Scan a single file and generate patches for findings."""
    result = {"file": filepath, "findings": [], "events": [], "error": None}
    try:
        findings = scan_file(filepath)
        if not findings:
            return result

        with open(filepath) as f:
            lines = f.readlines()

        for finding in findings:
            patch = generate_patch(finding, lines)
            event_path = emit(finding, patch)
            result["findings"].append(finding)
            result["events"].append(event_path)

    except Exception as e:
        result["error"] = str(e)
        log.error(f"Error scanning {filepath}: {e}")

    return result


def run_scan(target: str) -> ScanResult:
    """Run a full scan against a file or directory. Returns structured results."""
    scan_id = uuid.uuid4().hex[:12]
    scan = ScanResult(
        scan_id=scan_id,
        started_at=datetime.now(timezone.utc).isoformat(),
        target=target,
    )

    files = _collect_files(target)
    log.info(f"Scan {scan_id}: {len(files)} files to scan in {target}")

    workers = min(settings.scan.parallel_workers, len(files)) if files else 1

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_process_file, f): f for f in files}
        for future in as_completed(futures):
            filepath = futures[future]
            try:
                result = future.result()
                scan.files_scanned += 1
                if result["error"]:
                    scan.errors.append({"file": filepath, "error": result["error"]})
                scan.findings.extend(result["findings"])
                scan.events.extend(result["events"])
            except Exception as e:
                scan.errors.append({"file": filepath, "error": str(e)})

    scan.files_skipped = len(files) - scan.files_scanned
    scan.total_findings = len(scan.findings)
    scan.finished_at = datetime.now(timezone.utc).isoformat()
    scan.status = "completed"

    log.info(
        f"Scan {scan_id} complete: {scan.files_scanned} files, "
        f"{scan.total_findings} findings"
    )
    return scan
