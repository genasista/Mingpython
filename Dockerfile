FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    KMP_DUPLICATE_LIB_OK=TRUE \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

FROM base AS builder

# Build dependencies (removed in runtime stage)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential git curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.lock requirements.txt ./

RUN python -m venv /opt/venv

RUN --mount=type=cache,target=/root/.cache/pip \
    /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install --require-hashes -r requirements.lock

FROM base AS runtime

# Runtime-only OS dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 libsm6 libxext6 tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

COPY app ./app
RUN mkdir -p data/vector_db

EXPOSE 8001

# Healthcheck uses PORT env var (defaults to 8001)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import os, urllib.request; port=os.getenv('PORT', '8001'); urllib.request.urlopen(f'http://localhost:{port}/api/version1/health')"

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
# Port is set via PORT env var in entrypoint, default 8001
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8001}"]
