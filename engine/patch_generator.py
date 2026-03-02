"""LLM-powered patch generator. Uses Ollama for sovereign inference."""

import ollama

MODEL = "llama3.2:3b"


def generate_patch(finding: dict, source_lines: list[str]) -> str:
    """Generate a diff patch to add auth decorator to an unprotected route."""
    line_idx = finding["line"] - 1
    start = max(0, line_idx - 2)
    end = min(len(source_lines), line_idx + 5)
    context = "".join(source_lines[start:end])

    prompt = (
        f"You are a senior security engineer. "
        f"Add an @login_required decorator to the function `{finding['function']}` "
        f"in this code snippet. Return ONLY a unified diff patch, nothing else.\n\n"
        f"```python\n{context}```"
    )

    try:
        response = ollama.chat(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.message.content
    except Exception as e:
        return f"# Patch generation failed: {e}"
