# Antidote by PROOF

Sovereign infrastructure security for the PROOF Box.

Antidote deterministically scans Python web frameworks (FastAPI, Flask) for routes missing authentication decorators, generates remediation patches via local AI, and emits structured events for Comply/Viper integration.

## Architecture

```
                        ┌─────────────────────────────────────────────┐
                        │             Antidote Engine                  │
                        │                                             │
  Python files ──────>  │  Tree-sitter AST ──> Findings ──> AI Core  │
                        │  (deterministic)      (rules)    (patches)  │
                        │                                     │       │
                        │                          ┌──────────┤       │
                        │                          │          │       │
                        │                        MLX      Ollama      │
                        │                      (M4 Pro)   (M1 dev)    │
                        └──────────┬──────────────────────────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
              JSON Events     REST API      Web Dashboard
              (Comply/Viper)  (FastAPI)     (localhost:8740)
```

- **Discovery:** 100% deterministic via AST. No LLM in detection.
- **AI Core:** MLX (Metal native on M4) + Ollama fallback. Local-only. Sovereign.
- **Events:** Structured JSON for Comply and Viper integration.

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
ollama pull llama3.2:3b

# CLI scan
python antidote.py scan path/to/routes.py

# Batch scan a directory
python antidote.py scan-dir ./src

# Watch mode (continuous)
python antidote.py watch --dir src

# API server + web dashboard
python antidote.py serve
# Open http://localhost:8740
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | System health + AI status |
| POST | `/api/scan` | Scan a file or directory |
| GET | `/api/findings` | List all findings |
| GET | `/api/findings/{file}` | Get specific finding |
| GET | `/api/ai/status` | AI backend metrics |

## Docker (PROOF Box)

```bash
docker compose -f docker-compose.sovereign.yml up -d
# Dashboard at http://localhost:8740
```

Requires Ollama running on host.

## Configuration

Edit `antidote.yaml` or use environment variables:

```yaml
ai:
  backend: auto          # mlx | ollama | auto
  mlx_model: mlx-community/Mistral-7B-Instruct-v0.3-4bit
  ollama_model: llama3.2:3b
scan:
  exclude_dirs: [.venv, node_modules, __pycache__]
  parallel_workers: 4
events:
  event_dir: ./events/antidote
server:
  port: 8740
```

## Tests

```bash
pytest tests/ -v
```

## Hardware

- **M1 (dev):** 3B model via Ollama, <2 GB RAM, <5s per file
- **M4 Pro/Max (prod):** 7B+ via MLX Metal, background service, 100+ files/min

Built for Apple Silicon. Part of the PROOF ecosystem.
