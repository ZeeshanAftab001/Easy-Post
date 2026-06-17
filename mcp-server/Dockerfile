# MCP Server Dockerfile
FROM python:3.11-slim as builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt* ./
RUN if [ -f requirements.txt ]; then \
    pip install --user --no-cache-dir -r requirements.txt; \
    else \
    pip install --user --no-cache-dir pydantic fastapi uvicorn asyncpg redis; \
    fi

FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends postgresql-client curl && rm -rf /var/lib/apt/lists/*
RUN useradd -m -u 1000 appuser
COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1
COPY --chown=appuser:appuser . .
USER appuser
EXPOSE 9000
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:9000/health || exit 1
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "9000"]
