FROM python:3.12-slim AS builder

WORKDIR /app

ENV PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m pip wheel --wheel-dir=/wheels -r requirements.txt

FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN python -m pip install --no-index --find-links=/wheels -r requirements.txt \
    && rm -rf /wheels

COPY config.py main.py replies.txt ./
COPY commands ./commands
COPY handlers ./handlers
COPY utils ./utils

RUN mkdir -p /app/sessions /app/saved_media

VOLUME ["/app/sessions", "/app/saved_media"]

CMD ["python", "main.py"]
