"""Tests for the batch scanner module."""

import os
import tempfile
import shutil
from unittest.mock import patch

from engine.scanner import run_scan, _collect_files

VULN_CODE = """\
from fastapi import FastAPI
app = FastAPI()

@app.get("/users")
def list_users():
    return []
"""


def test_collect_files_single():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("x = 1")
        f.flush()
        files = _collect_files(f.name)
    os.unlink(f.name)
    assert len(files) == 1


def test_collect_files_directory():
    tmpdir = tempfile.mkdtemp()
    try:
        for name in ["a.py", "b.py", "c.txt"]:
            with open(os.path.join(tmpdir, name), "w") as f:
                f.write("x = 1")
        files = _collect_files(tmpdir)
        assert len(files) == 2  # only .py files
    finally:
        shutil.rmtree(tmpdir)


def test_collect_excludes_venv():
    tmpdir = tempfile.mkdtemp()
    try:
        venv_dir = os.path.join(tmpdir, ".venv")
        os.makedirs(venv_dir)
        with open(os.path.join(venv_dir, "lib.py"), "w") as f:
            f.write("x = 1")
        with open(os.path.join(tmpdir, "app.py"), "w") as f:
            f.write("x = 1")
        files = _collect_files(tmpdir)
        assert len(files) == 1
        assert files[0].endswith("app.py")
    finally:
        shutil.rmtree(tmpdir)


def test_run_scan_batch():
    tmpdir = tempfile.mkdtemp()
    try:
        with open(os.path.join(tmpdir, "routes.py"), "w") as f:
            f.write(VULN_CODE)
        with open(os.path.join(tmpdir, "helpers.py"), "w") as f:
            f.write("def util(): return 1\n")

        with patch("engine.scanner.generate_patch", return_value="# mock"):
            result = run_scan(tmpdir)

        assert result.status == "completed"
        assert result.files_scanned == 2
        assert result.total_findings == 1
        assert result.findings[0]["function"] == "list_users"
    finally:
        shutil.rmtree(tmpdir)
