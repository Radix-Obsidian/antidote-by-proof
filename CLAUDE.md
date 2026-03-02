# CLAUDE.md

## Project Overview
Antidote by PROOF: deterministic auth-gap scanner for Python web frameworks.
Pillar 3 of the PROOF ecosystem (Comply = Law, Viper = Ops, Antidote = Infra).

## Core Principle
- Detection: 100% deterministic via Tree-sitter AST. NO LLM.
- Patching: Local AI only (MLX on M4, Ollama fallback). Sovereign.

## Architecture
- `config.py` - Central YAML + env config (Pydantic)
- `engine/ai_core.py` - AI backend management (MLX/Ollama), health, metrics
- `engine/ast_parser.py` - Tree-sitter deterministic scanner
- `engine/patch_generator.py` - Routes through ai_core
- `engine/scanner.py` - Batch directory scanner with parallel processing
- `engine/logger.py` - Structured JSON logging
- `engine/rules/` - Extensible rule definitions
- `api/routes.py` - FastAPI REST API
- `api/models.py` - Pydantic request/response schemas
- `server.py` - FastAPI server entrypoint, serves frontend
- `events/emitter.py` - JSON event emitter for Comply/Viper
- `cli/watch.py` - Watchdog file watcher
- `frontend/` - Web dashboard (HTML/JS/CSS)
- `antidote.py` - Click CLI entrypoint

## Commands
```
python antidote.py scan <filepath>          # single file
python antidote.py scan-dir <directory>     # batch scan
python antidote.py watch --dir src          # watch mode
python antidote.py serve                    # API + dashboard on :8740
pytest tests/ -v                            # test suite
```

## Config
Edit `antidote.yaml` or set ANTIDOTE_* env vars. See config.py for schema.

## Prerequisites
- Python 3.12+ with venv
- Ollama with llama3.2:3b (M1) or MLX model (M4)
