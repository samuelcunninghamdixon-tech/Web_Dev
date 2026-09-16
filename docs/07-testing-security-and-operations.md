# Testing, Security, and Operations

## Test Layers

### Unit Tests

Cover parsers, URL validation, schema validation, state transition rules, prompt output parsing, HTML escaping, and configuration validation.

### Integration Tests

Run Postgres, the agent, scraper, and Ollama-compatible test doubles or local models. Verify real HTTP contracts, checkpoint writes, idempotency, and error propagation.

### Browser Tests

Use fixture pages for screenshots and generated output. Check responsive layouts, broken resources, console errors, and expected interactions.

### End-to-End Test

Run one safe prospect through discovery, scrape, audit, Slack approval, generation, validation, deployment to a test repository, and draft creation. Keep the final email send disabled.

## Security Controls

- Keep all secrets outside git and generated sites.
- Use least-privilege tokens and rotate them.
- Verify Slack signatures and internal service authentication.
- Block SSRF targets in the scraper.
- Restrict outbound network access where practical.
- Apply request size, page size, screenshot size, and execution time limits.
- Sanitize filenames and HTML inputs.
- Redact secrets and personal data in logs.
- Add retention and deletion procedures for screenshots, contact data, and generated sites.
- Do not automate outreach until consent, opt-out, and applicable law requirements are reviewed.

## Observability

Every request and workflow event should include a correlation ID, prospect ID, and thread ID when available. Record duration, status, retry count, model, and error category. Add health and readiness checks for each service.

Useful alerts include database unavailable, Ollama unavailable, repeated scrape timeouts, checkpoint failures, Slack signature failures, GitHub deployment failures, and n8n dead-letter growth.

## Backups and Recovery

1. Back up Postgres on a schedule.
2. Back up n8n workflow data and its encryption key.
3. Store generated artifacts according to a retention policy.
4. Document how to restore the database and reconnect checkpoints.
5. Test restoration rather than assuming backups work.

## Operational Runbook

For a failed workflow:

1. Find the correlation ID and prospect ID.
2. Inspect the agent state and n8n execution.
3. Classify the failure as transient, data-related, integration-related, or operator-actionable.
4. Retry only idempotent steps.
5. Repair the input or credential, then replay from the last valid checkpoint.
6. Confirm that no duplicate Slack message, deployment, or outreach draft was created.

## Release Gate

Before calling the service production-ready:

- all focused tests pass
- clean installation works from a new checkout
- secrets are absent from tracked files
- a full dry run succeeds
- restart recovery succeeds
- backups and restore have been tested
- outreach remains operator-approved
