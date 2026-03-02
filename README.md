# Antidote by PROOF

Sovereign infrastructure security for the PROOF Box.

Antidote deterministically scans Python web frameworks (FastAPI, Flask) for routes missing authentication decorators, generates remediation patches via local LLM, and emits structured events for Comply/Viper integration.

## Architecture

```
Python file → Tree-sitter AST (deterministic) → Findings → Ollama LLM (patch only) → JSON events
```

- **Discovery:** 100% deterministic via AST parsing. No LLM involved in detection.
- **Patching:** Ollama (llama3.2:3b on M1, 11B+ on M4 Pro/Max) generates diff patches.
- **Events:** Structured JSON emitted to `/events/antidote/` for Comply and Viper.

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
ollama pull llama3.2:3b

python antidote.py scan path/to/routes.py
python antidote.py watch --dir src
```

## Docker (PROOF Box)

```bash
docker compose -f docker-compose.sovereign.yml up -d
```

Requires Ollama running on host. Events are written to `./events/antidote/`.

## Tests

```bash
pip install pytest
pytest tests/ -v
```

## Event Format

```json
{
  "event": "antidote.finding",
  "timestamp": "2026-03-02T16:00:00+00:00",
  "file": "app/routes.py",
  "function": "list_users",
  "line": 12,
  "rule": "missing-auth-decorator",
  "severity": "CRITICAL",
  "patch": "...",
  "status": "unresolved"
}
```

## Hardware

- **M1 (dev):** 3B model, <2 GB RAM, <5s per file
- **M4 Pro/Max (prod):** 11B+ model, background service, 100+ files/min

Built for Apple Silicon. Part of the PROOF ecosystem.
