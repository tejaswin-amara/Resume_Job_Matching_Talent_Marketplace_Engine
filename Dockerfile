# Stage 1: Builder
FROM python:3.12-slim AS builder
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:0.6.5 /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev --no-editable
COPY . .

# Stage 2: Runtime
FROM python:3.12-slim AS runtime
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser
WORKDIR /app
COPY --from=builder /app /app
ENV PATH="/app/.venv/bin:$PATH"
USER appuser
EXPOSE 8000
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
