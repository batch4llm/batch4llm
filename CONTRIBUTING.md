# Contributing

## Prerequisites

- [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)
- Python >= 3.10 with `pip`
- Node.js >= 20 with `npm`

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/batch4llm/batch4llm.git
cd batch4llm
```

### 2. Backend – Python environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt -e "backend[dev]"
```

> `psycopg2` is intentionally excluded from local installs — it is only required inside Docker where PostgreSQL is available.

### 3. Frontend – Node dependencies

```bash
cd frontend
npm install
```

### 4. Pre-commit hooks

```bash
pre-commit install
```

This registers a Git hook that runs Black, Ruff, and ESLint automatically before every commit. If any check fails, the commit is aborted and the output shows what needs to be fixed.

## Running locally

```bash
docker compose -f compose.yaml -f compose.build.yaml -f compose.dev.yaml up -d --build
```

Everything runs via Docker. The frontend uses Vite with HMR and is available at `http://localhost:80`. Changes in `frontend/src` are reflected immediately in the browser.

## Tests

```bash
cd backend
pytest
```

## Linting

The pre-commit hook checks linting automatically on every commit. To run manually:

```bash
# Backend
ruff check src
black --check src

# Frontend
cd frontend && npm run lint
```

To auto-fix:

```bash
# Backend
ruff check --fix src
black src

# Frontend
cd frontend && npx eslint --fix .
```
