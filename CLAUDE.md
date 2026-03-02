# CLAUDE.md

## Project Overview
Antidote by PROOF: deterministic auth-gap scanner for Python web frameworks.
Uses Tree-sitter AST parsing (NO LLM) for vulnerability detection.
Uses Ollama LLM ONLY for generating remediation patches.

## Architecture
- `engine/ast_parser.py` - Tree-sitter based deterministic scanner
- `engine/patch_generator.py` - Ollama LLM patch writer
- `engine/rules/` - Rule definitions (auth decorators, etc.)
- `events/emitter.py` - JSON event emitter for Comply/Viper
- `cli/watch.py` - Watchdog file watcher
- `antidote.py` - Click CLI entrypoint

## Commands
```
python antidote.py scan <filepath>
python antidote.py watch --dir src
pytest tests/ -v
```

## Prerequisites
- Python 3.12+ with venv
- Ollama with llama3.2:3b pulled
