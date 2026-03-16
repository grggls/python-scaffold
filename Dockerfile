# Stage 1: Build dependencies
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-editable

COPY src/ ./src/
RUN uv sync --frozen --no-dev

# Stage 2: Runtime
FROM python:3.12-slim

RUN groupadd -r appuser && useradd -r -g appuser appuser

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

ENV PATH="/app/.venv/bin:$PATH"
WORKDIR /app

USER appuser

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD ["python", "-m", "myproject.main", "--version"]

ENTRYPOINT ["python", "-m", "myproject.main"]
