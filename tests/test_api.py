"""Integration tests for the Antidote REST API."""

import os
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

VULN_CODE = """\
from fastapi import FastAPI
app = FastAPI()

@app.get("/public")
def public_endpoint():
    return {"status": "ok"}

@app.post("/data")
def post_data():
    return {"status": "created"}
"""


def test_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert "status" in data
    assert "version" in data
    assert "ai" in data


def test_ai_status_endpoint():
    res = client.get("/api/ai/status")
    assert res.status_code == 200
    data = res.json()
    assert "backend_config" in data
    assert "mlx" in data
    assert "ollama" in data
    assert "metrics" in data


def test_scan_file():
    """Scan a single vulnerable file via API."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(VULN_CODE)
        f.flush()
        filepath = f.name

    try:
        # Mock at the import site to avoid needing Ollama/MLX in tests
        with patch("engine.patch_generator.ai_generate", return_value="# mock patch"):
            res = client.post("/api/scan", json={"target": filepath})

        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "completed"
        assert data["total_findings"] == 2
        assert data["files_scanned"] == 1

        func_names = {f["function"] for f in data["findings"]}
        assert "public_endpoint" in func_names
        assert "post_data" in func_names
    finally:
        os.unlink(filepath)


def test_scan_directory():
    """Scan a directory with multiple files via API."""
    tmpdir = tempfile.mkdtemp()
    try:
        vuln_file = os.path.join(tmpdir, "routes.py")
        with open(vuln_file, "w") as f:
            f.write(VULN_CODE)

        safe_file = os.path.join(tmpdir, "utils.py")
        with open(safe_file, "w") as f:
            f.write("def helper(): return 42\n")

        with patch("engine.patch_generator.ai_generate", return_value="# mock patch"):
            res = client.post("/api/scan", json={"target": tmpdir})

        assert res.status_code == 200
        data = res.json()
        assert data["files_scanned"] == 2
        assert data["total_findings"] == 2
    finally:
        shutil.rmtree(tmpdir)


def test_scan_nonexistent_path():
    res = client.post("/api/scan", json={"target": "/nonexistent/path"})
    assert res.status_code == 404


def test_findings_endpoint():
    res = client.get("/api/findings")
    assert res.status_code == 200
    data = res.json()
    assert "findings" in data
    assert "total" in data


def test_landing_served():
    res = client.get("/")
    assert res.status_code == 200
    assert "Antidote" in res.text


def test_dashboard_served():
    res = client.get("/dashboard")
    assert res.status_code == 200
    assert "Antidote" in res.text
