# ──────────────────────────────────────────────
# Stage 1: Install dependencies in a builder
# ──────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

COPY requirements.prod.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.prod.txt

# ──────────────────────────────────────────────
# Stage 2: Production runtime
# ──────────────────────────────────────────────
FROM python:3.12-slim AS runtime

# Prevent Python from writing .pyc files and enable unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create a non-root user
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY alembic.ini .
COPY alembic ./alembic
COPY app ./app
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# alembic needs write access to its tmp directory
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

LABEL org.opencontainers.image.source="https://github.com/shanto78/techblog-python-vue" \
      org.opencontainers.image.title="techblog-backend" \
      org.opencontainers.image.description="TechBlog FastAPI backend"

ENTRYPOINT ["/docker-entrypoint.sh"]
