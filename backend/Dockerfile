# Stage 0: Dev
FROM python:3.11-slim AS dev

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt psycopg2

COPY pyproject.toml ./
COPY src ./src
RUN pip install -e .

CMD ["uvicorn", "batch4llm.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Stage 1: Backend Wheel Build
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel && \
    pip wheel --requirement requirements.txt -w /app/wheels

COPY pyproject.toml ./
COPY src ./src

RUN pip wheel --prefer-binary -w /app/wheels psycopg2 && \
    pip wheel --no-deps --prefer-binary -w /app/wheels .

# Stage 2: Serve
FROM python:3.11-slim AS serve

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache-dir /wheels/*
