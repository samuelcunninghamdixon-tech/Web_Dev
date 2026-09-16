# Current Scaffold Gaps

This file records the known difference between the current repository and a fully functional service. Use it as the implementation backlog.

## Infrastructure

- Add persistent shared mounts for screenshots, assets, exports, and generated sites.
- Add a real database migration strategy and Postgres readiness checks.
- Configure n8n authentication, encryption, persistent data, and HTTPS callback support.
- Add health and readiness endpoints to every service.
- Add secrets management for deployments.

## Agent Service

- Register the routers in `services/agent/main.py`.
- Replace placeholder route responses with typed request handling.
- Build the compiled LangGraph workflow and configure `AsyncPostgresSaver`.
- Add the actual audit, Slack, revision, and code generation transitions.
- Add internal authentication and idempotency.

## Scraper Service

- Implement the `/scrape` endpoint.
- Add Playwright browser management and Chromium installation in the container.
- Implement extraction, Wappalyzer integration, SSRF protection, and shared artifact storage.

## Code Generation

- Move generation behind a service endpoint.
- Make the Ollama image encoding and response parsing match the Ollama API contract.
- Improve browser validation so resource failures are actually observed rather than skipped.
- Handle GitHub existing-file updates using the current file SHA.
- Add approval checks before deployment.

## Workflows and Tests

- Replace placeholder n8n URLs and configure credentials through n8n.
- Add real request bodies and field mappings between workflows and services.
- Replace placeholder tests with fixture-backed unit, integration, browser, and end-to-end tests.
- Add structured logging, metrics, retries, and failure notifications.

## Immediate Next Work Session

1. Fix application settings and database URL handling.
2. Implement Postgres migrations and service readiness checks.
3. Implement the scraper endpoint with a local fixture test.
4. Run `docker compose config` and the focused test suite.
5. Only then connect the first n8n discovery workflow.
