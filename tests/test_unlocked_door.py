"""Test suite for Antidote auth-gap scanner."""

import os
import tempfile
from engine.ast_parser import scan_file


VULN_CODE = """\
from fastapi import FastAPI
app = FastAPI()

@app.get("/public")
def public_endpoint():
    return {"status": "ok"}

@app.get("/admin")
@login_required
def admin_endpoint():
    return {"status": "secret"}

@app.post("/data")
def post_data():
    return {"status": "created"}
"""

SAFE_CODE = """\
from fastapi import FastAPI
app = FastAPI()

@app.get("/admin")
@login_required
def admin_endpoint():
    return {"status": "secret"}
"""

NO_ROUTES_CODE = """\
def helper():
    return 42

class Service:
    def run(self):
        pass
"""


def test_finds_unprotected_routes():
    """Scanner should find routes missing auth decorators."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(VULN_CODE)
        f.flush()
        findings = scan_file(f.name)
    os.unlink(f.name)

    assert len(findings) == 2
    func_names = {f["function"] for f in findings}
    assert "public_endpoint" in func_names
    assert "post_data" in func_names


def test_no_false_positives_on_protected():
    """Scanner should NOT flag routes that have auth decorators."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(SAFE_CODE)
        f.flush()
        findings = scan_file(f.name)
    os.unlink(f.name)

    assert len(findings) == 0


def test_no_findings_without_routes():
    """Scanner should return empty list for files without route decorators."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(NO_ROUTES_CODE)
        f.flush()
        findings = scan_file(f.name)
    os.unlink(f.name)

    assert len(findings) == 0


def test_finding_structure():
    """Each finding should have the expected fields."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(VULN_CODE)
        f.flush()
        findings = scan_file(f.name)
    os.unlink(f.name)

    for finding in findings:
        assert "file" in finding
        assert "function" in finding
        assert "line" in finding
        assert "rule" in finding
        assert finding["rule"] == "missing-auth-decorator"
        assert finding["severity"] == "CRITICAL"
