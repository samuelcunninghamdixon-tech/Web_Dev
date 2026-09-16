# Local Environment and Configuration

## Prerequisites

Install and verify:

- Docker Desktop with Compose
- Git
- Python 3.11
- Node.js/npm if using n8n tooling or frontend utilities
- A browser supported by Playwright
- Enough disk space for Postgres data, screenshots, generated sites, and Ollama models

## Initial Setup

```powershell
Copy-Item .env.example .env
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r services/agent/requirements.txt
pip install -r services/scraper/requirements.txt
pip install -r services/codegen/requirements.txt
playwright install chromium
docker compose config
```

`docker compose config` should fail if required interpolation or YAML configuration is invalid. Do not continue until it renders successfully.

## Environment Groups

### Application

- `APP_ENV`
- `PROJECT_NAME`
- `SHARED_ROOT`

### Database

- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `DATABASE_URL`

Use a URL format compatible with the selected async driver. The current agent code must standardize whether it uses `postgresql://` or `postgresql+asyncpg://` before production use.

### Local Models

- `OLLAMA_BASE_URL`
- `VISION_MODEL`
- `CODER_MODEL`
- `TEXT_MODEL`

Pull and verify models deliberately. Do not download all models automatically during every container start.

```powershell
docker compose up -d postgres ollama n8n
# Run model pulls from the Ollama container or local Ollama installation.
```

### Integrations

- Slack: `SLACK_WEBHOOK_URL`, `SLACK_SIGNING_SECRET`
- GitHub: `GITHUB_TOKEN`, `GITHUB_OWNER`, `GITHUB_REPO`
- Email: SMTP or Resend values
- Discovery: provider-specific endpoint and key

## Configuration Rules

1. Keep `.env.example` complete but secret-free.
2. Validate settings at service startup with typed configuration.
3. Fail clearly when a required production setting is missing.
4. Use separate development and production credentials.
5. Redact tokens, authorization headers, cookies, and personal contact data from logs.
6. Use absolute or configured shared paths consistently across host and containers.

## Local Smoke Checks

```powershell
docker compose ps
Invoke-WebRequest http://localhost:8001/health
Invoke-WebRequest http://localhost:5678
```

Also run `Invoke-WebRequest http://localhost:8002/health` for the scraper service. The agent and scraper containers currently expose only placeholder health endpoints. Treat successful health responses as infrastructure checks, not proof that the business workflow is implemented.
