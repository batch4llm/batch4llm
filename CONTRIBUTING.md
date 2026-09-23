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

Or simply `make dev` (see [Makefile](Makefile) for shortcuts, incl. `make test` and `make lint`).

Everything runs via Docker. The frontend uses Vite with HMR and is available at `http://localhost:80`. Changes in `frontend/src` are reflected immediately in the browser.

## Database migrations

Schema changes are managed with Alembic. `docker compose up` (and `make dev`) always applies pending migrations automatically via the `migrate` service before `backend`/`worker`/`beat` start — you no longer need to drop and recreate your local Postgres.

After changing a model in `backend/src/batch4llm/manager/database/models/`, generate a migration against the running dev stack and commit the result:

```bash
docker compose -f compose.yaml -f compose.build.yaml -f compose.dev.yaml exec backend b4llm db revision --autogenerate -m "add foo column"
```

Review the generated file under `backend/src/batch4llm/migrations/versions/` before committing — Alembic's autogenerate doesn't always get everything right (e.g. data migrations, some enum/constraint changes).

Other useful commands (run the same way, via `exec backend b4llm db ...`): `current`, `history`, `downgrade <rev>`, `stamp <rev>`.

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
