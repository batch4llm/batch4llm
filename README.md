Batch4LLM is an all-in-one solution for scientific file evaluation using LLMs. It provides a web dashboard to easily create and manage batches with different models and settings, and to access and export results efficiently. It also supports existing batch APIs from supported providers (OpenAI, Google), allowing you to process large numbers of files without the need for a constantly running server, while reducing API costs (see [Roadmap](#roadmap)).   

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
   curl -L https://raw.githubusercontent.com/Benjino16/batch4llm/main/compose.yaml -o compose.yaml
```

3. Start the service:
```
   docker compose up -d
```


## Setup (Build from Repository)

### Prerequisites

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

### Steps

1. **Clone the repository:**
  ```bash
   git clone https://github.com/Benjino16/batch4llm.git
  ```
2. **Navigate to the project directory:**
  ```bash
   cd batch4llm
  ```
3. **Build/Start the service:**
  ```bash
   docker compose -f compose.yaml -f compose.build.yaml up -d
  ```
