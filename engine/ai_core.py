"""AI backend management — health checks, model routing, metrics."""

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone

from config import settings
from engine.logger import log


@dataclass
class AIMetrics:
    total_requests: int = 0
    total_failures: int = 0
    total_tokens_est: int = 0
    total_latency_ms: float = 0
    last_backend_used: str = ""
    last_request_at: str = ""
    mlx_available: bool | None = None
    ollama_available: bool | None = None


_metrics = AIMetrics()


def get_metrics() -> dict:
    avg_latency = (
        _metrics.total_latency_ms / _metrics.total_requests
        if _metrics.total_requests > 0
        else 0
    )
    return {
        "total_requests": _metrics.total_requests,
        "total_failures": _metrics.total_failures,
        "avg_latency_ms": round(avg_latency, 1),
        "last_backend_used": _metrics.last_backend_used,
        "last_request_at": _metrics.last_request_at,
        "mlx_available": _metrics.mlx_available,
        "ollama_available": _metrics.ollama_available,
    }


def check_mlx() -> bool:
    try:
        from mlx_lm import load
        _metrics.mlx_available = True
        return True
    except Exception:
        _metrics.mlx_available = False
        return False


def check_ollama() -> bool:
    try:
        import ollama
        ollama.list()
        _metrics.ollama_available = True
        return True
    except Exception:
        _metrics.ollama_available = False
        return False


def health_check() -> dict:
    """Full health report for the AI subsystem."""
    mlx_ok = check_mlx()
    ollama_ok = check_ollama()
    backend = settings.ai.backend

    if backend == "auto":
        ready = mlx_ok or ollama_ok
    elif backend == "mlx":
        ready = mlx_ok
    else:
        ready = ollama_ok

    return {
        "status": "healthy" if ready else "degraded",
        "backend_config": backend,
        "mlx": {"available": mlx_ok, "model": settings.ai.mlx_model},
        "ollama": {"available": ollama_ok, "model": settings.ai.ollama_model},
        "metrics": get_metrics(),
    }


def generate(prompt: str, finding: dict) -> str:
    """Route generation to the active backend with metrics tracking."""
    backend = settings.ai.backend
    start = time.time()
    result = None
    used_backend = None

    try:
        if backend == "mlx":
            result = _mlx_generate(prompt, finding)
            used_backend = "mlx"
        elif backend == "ollama":
            result = _ollama_generate(prompt)
            used_backend = "ollama"
        else:
            # auto: try MLX first, fall back to Ollama
            try:
                result = _mlx_generate(prompt, finding)
                used_backend = "mlx"
            except Exception:
                result = _ollama_generate(prompt)
                used_backend = "ollama"

        elapsed = (time.time() - start) * 1000
        _metrics.total_requests += 1
        _metrics.total_latency_ms += elapsed
        _metrics.last_backend_used = used_backend
        _metrics.last_request_at = datetime.now(timezone.utc).isoformat()

        log.info(
            f"AI patch generated via {used_backend} in {elapsed:.0f}ms",
            extra={"data": {"backend": used_backend, "latency_ms": round(elapsed, 1)}},
        )
        return result

    except Exception as e:
        _metrics.total_failures += 1
        log.error(f"AI generation failed: {e}")
        return f"# Patch generation failed: {e}"


def _mlx_generate(prompt: str, finding: dict) -> str:
    from mlx_lm import load, generate as mlx_gen

    model, tokenizer = load(settings.ai.mlx_model)
    response = mlx_gen(
        model, tokenizer,
        prompt=prompt,
        max_tokens=settings.ai.max_tokens,
        temp=settings.ai.temperature,
    )
    patch = response.strip()
    if not patch.startswith("---"):
        patch = f"--- a/{finding['file']}\n+++ b/{finding['file']}\n{patch}"
    return patch


def _ollama_generate(prompt: str) -> str:
    import ollama

    response = ollama.chat(
        model=settings.ai.ollama_model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.message.content
