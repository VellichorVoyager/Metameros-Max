# Metameros-Max

Agent scaffold for building and deploying AI agents on the [DigitalOcean Gradient AI Platform](https://docs.digitalocean.com/products/gradient/).

## Overview

This repository provides a lightweight Python SDK and CLI (`gradient_adk`) for:
- Scaffolding agent entrypoints with the `@entrypoint` decorator
- Running agents locally on an HTTP server (`POST /run`, `GET /health`)
- Deploying agents to the Gradient platform
- Fetching traces and logs for deployed agents

## Prerequisites

- Python 3.10+
- A DigitalOcean [Model Access Key](https://cloud.digitalocean.com/api/tokens) (required for deploy/traces/logs)

## Local Development

```bash
# Install the package in editable mode
pip install -e .

# Scaffold a starter agent in the current directory
gradient agent init .

# Run the local development server (default: port 8080)
gradient agent run --module agent:entry
```

The server exposes:
- `POST /run` — invoke the agent entrypoint with a JSON body `{"payload": {...}, "context": {...}}`
- `GET /health` — liveness check; returns `{"status": "ok"}`

## Required Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GRADIENT_API_KEY` | Yes (for deploy/traces/logs) | DigitalOcean Gradient Model Access Key |
| `PORT` | No (default `8080`) | Port the server listens on — set automatically by App Platform |

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
# edit .env with your GRADIENT_API_KEY
```

> **Never commit your `.env` file.** It is already in `.gitignore`.

## Run Command

```bash
gradient agent run --module agent:entry
```

To specify a custom host/port:

```bash
gradient agent run --module agent:entry --host 0.0.0.0 --port 8080
```

The `--port` flag defaults to the `PORT` environment variable (falling back to `8080`), so DigitalOcean App Platform injects the correct port automatically.

## Test Command

```bash
python -m unittest discover -s tests -v
```

## Deployment — DigitalOcean App Platform

### 1. Set the required secret

In your DigitalOcean App Platform dashboard, add the following environment variable as a **secret**:

```
GRADIENT_API_KEY = <your-model-access-key>
```

### 2. Configure the run command

In the App Platform **Run Command** field, set:

```
gradient agent run --module agent:entry
```

The platform will inject `PORT` automatically. The server binds to `0.0.0.0:$PORT`.

### 3. Health check

App Platform will hit `GET /health` to confirm the service is healthy. No additional configuration is needed — the endpoint is built in.

### 4. CLI-based deploy (optional)

To deploy directly from the CLI:

```bash
export GRADIENT_API_KEY=<your-key>
gradient agent configure --api-key $GRADIENT_API_KEY
gradient agent deploy --module agent:entry --name my-agent --region nyc3
```

After a successful deploy, the Agent ID is saved to `~/.gradient/config.json` and picked up automatically by `traces` and `logs` commands.

### 5. View traces and logs

```bash
gradient agent traces
gradient agent logs --follow
```

## Fail-fast env validation

For agents that require `GRADIENT_API_KEY` at startup, call `validate_required_env` in your agent module:

```python
from gradient_adk import entrypoint, validate_required_env

validate_required_env("GRADIENT_API_KEY")

@entrypoint
def entry(payload, context):
    ...
```

If the variable is unset the process exits immediately with a clear error message instead of failing on the first API call.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Error: Model Access Key not set.` | Set `GRADIENT_API_KEY` in your environment or run `gradient agent configure --api-key <key>` |
| `Error: Agent ID not set.` | Pass `--agent-id <id>` or run `gradient agent configure --agent-id <id>` |
| `404` on POST /run | Ensure you are posting to `/run`, not `/` |
| Port already in use | Change the port with `--port` or set the `PORT` env var |
| App Platform health check failing | Confirm run command is `gradient agent run --module agent:entry` and `GET /health` returns 200 |
