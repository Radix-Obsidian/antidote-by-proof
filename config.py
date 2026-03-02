"""Centralized configuration for Antidote. Loads from antidote.yaml + env vars."""

import os
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

CONFIG_PATH = os.environ.get("ANTIDOTE_CONFIG", "./antidote.yaml")


class AIConfig(BaseModel):
    backend: str = Field(default="auto", description="mlx | ollama | auto")
    mlx_model: str = "mlx-community/Mistral-7B-Instruct-v0.3-4bit"
    ollama_model: str = "llama3.2:3b"
    ollama_host: str = "http://localhost:11434"
    max_tokens: int = 512
    temperature: float = 0.1


class ScanConfig(BaseModel):
    extensions: list[str] = [".py"]
    exclude_dirs: list[str] = [".venv", "node_modules", "__pycache__", ".git", "dist", "build"]
    exclude_files: list[str] = []
    max_file_size_kb: int = 500
    parallel_workers: int = 4


class EventConfig(BaseModel):
    event_dir: str = "./events/antidote"


class ServerConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8740
    reload: bool = False


class Config(BaseModel):
    ai: AIConfig = AIConfig()
    scan: ScanConfig = ScanConfig()
    events: EventConfig = EventConfig()
    server: ServerConfig = ServerConfig()


def load_config() -> Config:
    """Load config from YAML file, then override with environment variables."""
    data = {}
    config_path = Path(CONFIG_PATH)
    if config_path.exists():
        with open(config_path) as f:
            data = yaml.safe_load(f) or {}

    config = Config(**data)

    # Environment overrides take priority
    if v := os.environ.get("ANTIDOTE_BACKEND"):
        config.ai.backend = v
    if v := os.environ.get("ANTIDOTE_MLX_MODEL"):
        config.ai.mlx_model = v
    if v := os.environ.get("ANTIDOTE_OLLAMA_MODEL"):
        config.ai.ollama_model = v
    if v := os.environ.get("OLLAMA_HOST"):
        config.ai.ollama_host = v
    if v := os.environ.get("ANTIDOTE_EVENT_DIR"):
        config.events.event_dir = v
    if v := os.environ.get("ANTIDOTE_PORT"):
        config.server.port = int(v)

    return config


# Singleton — import this everywhere
settings = load_config()
