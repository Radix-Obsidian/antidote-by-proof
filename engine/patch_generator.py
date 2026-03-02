"""LLM-powered patch generator. MLX native on Apple Silicon, Ollama fallback."""

import os

BACKEND = os.environ.get("ANTIDOTE_BACKEND", "auto")
MLX_MODEL = os.environ.get("ANTIDOTE_MLX_MODEL", "mlx-community/Mistral-7B-Instruct-v0.3-4bit")
OLLAMA_MODEL = os.environ.get("ANTIDOTE_OLLAMA_MODEL", "llama3.2:3b")


def _build_prompt(finding: dict, source_lines: list[str]) -> str:
    line_idx = finding["line"] - 1
    start = max(0, line_idx - 2)
    end = min(len(source_lines), line_idx + 5)
    context = "".join(source_lines[start:end])

    return (
        f"You are a senior security engineer. Fix this unlocked door.\n"
        f"File: {finding['file']}\n"
        f"Function: {finding['function']} (line {finding['line']})\n"
        f"Add the missing auth decorator (@login_required) above the route.\n"
        f"Return ONLY a clean unified diff (--- +++ @@ format). "
        f"No explanation. No markdown. Just the patch.\n\n"
        f"```python\n{context}```"
    )


def _generate_mlx(prompt: str, finding: dict) -> str:
    from mlx_lm import load, generate

    model, tokenizer = load(MLX_MODEL)
    response = generate(model, tokenizer, prompt=prompt, max_tokens=512, temp=0.1)
    patch = response.strip()
    if not patch.startswith("---"):
        patch = f"--- a/{finding['file']}\n+++ b/{finding['file']}\n{patch}"
    return patch


def _generate_ollama(prompt: str) -> str:
    import ollama

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.message.content


def generate_patch(finding: dict, source_lines: list[str]) -> str:
    """Generate a unified diff patch. Uses MLX on Apple Silicon, Ollama as fallback."""
    prompt = _build_prompt(finding, source_lines)

    if BACKEND == "mlx":
        return _generate_mlx(prompt, finding)

    if BACKEND == "ollama":
        return _generate_ollama(prompt)

    # auto: try MLX first (fast on M4), fall back to Ollama (works everywhere)
    try:
        return _generate_mlx(prompt, finding)
    except Exception:
        pass

    try:
        return _generate_ollama(prompt)
    except Exception as e:
        return f"# Patch generation failed: {e}"
