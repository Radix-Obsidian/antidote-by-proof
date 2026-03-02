"""LLM-powered patch generator. Routes through AI core for metrics and health."""

from engine.ai_core import generate as ai_generate


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


def generate_patch(finding: dict, source_lines: list[str]) -> str:
    """Generate a unified diff patch via the AI core."""
    prompt = _build_prompt(finding, source_lines)
    return ai_generate(prompt, finding)
