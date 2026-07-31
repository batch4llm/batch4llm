<br>

> [!WARNING]
> This project is still in development and does not have a stable release yet. It is **not recommended** to run an instance on a publicly accessible server. Usage costs will apply when using commercial API backends.

<br>

## Setup (with Pre-built Docker Images)
This is recommended for production.

### Prerequisites

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

### Steps

1. Create a directory for the service:
```
   mkdir batch4llm
   cd batch4llm
```
2. Place the [compose.yaml](/compose.yaml) file inside this directory.
```
   curl -L https://raw.githubusercontent.com/batch4llm/batch4llm/main/compose.yaml -o compose.yaml
```

3. Start the service:
```
   docker compose up -d
```

### HTTPS

By default, Traefik only serves plain HTTP on port 80. To enable HTTPS via Let's Encrypt, set `DOMAIN` and `ACME_EMAIL` in your `.env` (see `.env.example`) and start with the `compose.prod.yaml` override:
```
   docker compose -f compose.yaml -f compose.prod.yaml up -d
```
This adds a `websecure` (443) entrypoint with automatic certificates and redirects plain HTTP traffic to HTTPS. `DOMAIN` must be a public hostname that resolves to this server, since Let's Encrypt validates ownership over port 80.


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
