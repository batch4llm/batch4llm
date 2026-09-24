<br>

> [!WARNING]
> This project is still in development and does not have a stable release yet. It is **not recommended** to run an instance on a publicly accessible server. Usage costs will apply when using commercial API backends.

<br>

## Setup (Production Server)
Runs the pre-built Docker images with HTTPS via Let's Encrypt. This is recommended for production.

### Prerequisites

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- A public hostname (`DOMAIN`) that resolves to the server, with ports 80 and 443 reachable (Let's Encrypt validates ownership over port 80)

### Steps

1. Create a directory for the service:
```
   mkdir batch4llm
   cd batch4llm
```
2. Download the production compose file and the example environment file:
```
   curl -L https://raw.githubusercontent.com/batch4llm/batch4llm/main/compose.prod.yaml -o compose.yaml
   curl -L https://raw.githubusercontent.com/batch4llm/batch4llm/main/.env.example -o .env
```
3. Edit `.env`: replace every `change_me` with a real value (e.g. generated via `openssl rand -hex 24`), set `DOMAIN` and `ACME_EMAIL`, and pin `BATCH4LLM_VERSION` to a [release](https://github.com/batch4llm/batch4llm/releases) such as `v0.1.0`.

4. Start the service:
```
   docker compose up -d
```

All services restart automatically after a reboot. Data lives in the named Docker volumes `batch4llm_postgres_data`, `batch4llm_minio_data`, `batch4llm_redis_data` and `batch4llm_letsencrypt`.

### Updating

Set `BATCH4LLM_VERSION` in `.env` to the new release, then:
```
   docker compose pull
   docker compose up -d
```
Database migrations run automatically on startup (via the `migrate` service) before the backend and workers start. If a release changes `compose.prod.yaml` itself, download it again as in step 2 (your `.env` stays untouched).

### Admin account

Set `ADMIN_USERNAME` and `ADMIN_PASSWORD` in your `.env` (see `.env.example`) before the first `docker compose up` to have an admin account created automatically. This only happens once — an existing account with that username is never modified on later restarts.

If you skip this, create the first admin manually instead:
```
   docker compose exec backend b4llm user create <username> <password> --admin
```

## Local Quick Start (Pre-built Images, HTTP)
To try batch4llm on your own machine without a domain, use the plain [compose.yaml](/compose.yaml). It serves HTTP on port 80 and is meant for `http://localhost` only — login cookies are marked `Secure`, which browsers accept over plain HTTP only on `localhost`.

```
   mkdir batch4llm && cd batch4llm
   curl -L https://raw.githubusercontent.com/batch4llm/batch4llm/main/compose.yaml -o compose.yaml
   curl -L https://raw.githubusercontent.com/batch4llm/batch4llm/main/.env.example -o .env
   # replace every change_me in .env
   docker compose up -d
```
Then open http://localhost.


## Setup (Build from Repository)

### Prerequisites

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

### Steps

1. **Clone the repository:**
  ```bash
   git clone https://github.com/batch4llm/batch4llm.git
  ```
2. **Navigate to the project directory:**
  ```bash
   cd batch4llm
  ```
3. **Build/Start the service:**
  ```bash
   docker compose -f compose.yaml -f compose.build.yaml up -d
  ```
