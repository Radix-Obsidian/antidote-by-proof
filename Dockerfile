FROM python:3.12-slim

LABEL org.opencontainers.image.title="Antidote by PROOF"
LABEL org.opencontainers.image.description="Sovereign auth-gap scanner for Python web frameworks"
LABEL org.opencontainers.image.vendor="PROOF"
LABEL org.opencontainers.image.source="https://github.com/Radix-Obsidian/antidote-by-proof"
LABEL org.opencontainers.image.licenses="Proprietary"
LABEL proof.pillar="antidote"
LABEL proof.port="8740"

WORKDIR /app

# Install dependencies (strip mlx-lm — Apple Silicon only, Ollama used in Docker)
COPY requirements.txt .
RUN grep -v mlx-lm requirements.txt > /tmp/requirements-docker.txt && \
    pip install --no-cache-dir -r /tmp/requirements-docker.txt && \
    rm /tmp/requirements-docker.txt

COPY . .

# Non-root user for production
RUN useradd --system --no-create-home antidote && \
    chown -R antidote:antidote /app && \
    mkdir -p /events/antidote && chown antidote:antidote /events /events/antidote

USER antidote

EXPOSE 8740

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8740/api/health')" || exit 1

ENTRYPOINT ["python", "antidote.py"]
CMD ["serve"]
