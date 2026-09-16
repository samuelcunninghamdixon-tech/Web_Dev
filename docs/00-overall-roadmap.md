# Overall Roadmap

This project should be built as a staged local pipeline. Each stage must be working and observable before the next one is added.

## Target Flow

```text
Prospect source
  -> n8n discovery workflow
  -> scraper service
  -> Postgres prospect record
  -> agent audit graph
  -> Slack human review
  -> design brief revision
  -> code generation and browser validation
  -> GitHub Pages preview
  -> outreach draft
```

## Milestones

### 1. External setup and local prerequisites

Complete [01-external-accounts-and-keys.md](01-external-accounts-and-keys.md) and [02-local-environment.md](02-local-environment.md). Do not put real secrets in git.

**Exit check:** Docker, Git, Python, Node/npm, and Playwright are available; required external accounts exist; `.env` is populated locally.

### 2. Platform foundation

Implement database migrations, application settings, structured logging, health checks, shared storage, and service-to-service configuration.

**Exit check:** `docker compose up --build` starts Postgres, Ollama, n8n, agent, and scraper; health endpoints respond; database tables exist.

### 3. Scraper service

Follow [03-scraper-service.md](03-scraper-service.md). Build URL validation, browser lifecycle handling, screenshots, asset extraction, contact extraction, and technology detection.

**Exit check:** a known test URL produces deterministic JSON and a screenshot within the timeout, with browser processes closed afterward.

### 4. Audit and human review

Follow [04-agent-and-slack-review.md](04-agent-and-slack-review.md). Add the LangGraph state machine, Ollama vision calls, Postgres checkpointing, Slack signature verification, and approval transitions.

**Exit check:** an audit can pause for review, survive an agent restart, and resume from an approved or revision-requested Slack event.

### 5. Code generation and preview deployment

Follow [05-codegen-and-deployment.md](05-codegen-and-deployment.md). Generate HTML from a validated brief, run Playwright checks, repair failures, and deploy only approved output.

**Exit check:** an approved prospect produces a browser-valid GitHub Pages preview URL.

### 6. n8n orchestration and outreach

Follow [06-n8n-workflows-and-outreach.md](06-n8n-workflows-and-outreach.md). Import workflows, configure credentials, add retries and deduplication, and create drafts rather than sending email automatically at first.

**Exit check:** one complete dry run exists from discovery through outreach draft.

### 7. Hardening and operations

Follow [07-testing-security-and-operations.md](07-testing-security-and-operations.md). Add automated tests, rate limits, audit trails, backups, monitoring, retention rules, and an operator runbook.

**Exit check:** failures are visible, recoverable, and do not silently contact a prospect or expose credentials.

## Recommended Build Order

1. External accounts and `.env` setup
2. Postgres schema and migrations
3. Service health endpoints and structured configuration
4. Scraper implementation
5. Ollama client and strict response parsing
6. LangGraph persistence and pause/resume behavior
7. Slack events and review actions
8. Code generation and validation
9. GitHub Pages deployment
10. n8n workflows
11. Outreach drafts and approval controls
12. Tests, security, observability, and backups

## Definition of Done

The service is fully functional when it can process a real prospect through the complete flow, persist every state transition, require human approval before generation and outreach, validate generated pages in a browser, deploy an approved preview, and recover after restarting any one service.
