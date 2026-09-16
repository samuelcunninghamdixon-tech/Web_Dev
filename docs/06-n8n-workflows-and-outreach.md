# n8n Workflows and Outreach

## Goal

Use n8n for scheduling, integration, retries, and operator visibility while keeping business decisions and durable state in the agent service and database.

## Step 1: Configure n8n

1. Start n8n with persistent storage.
2. Configure its Postgres connection separately from the application checkpoint tables when practical.
3. Enable authentication before exposing the editor.
4. Set a stable encryption key and back it up securely.
5. Configure webhook base URLs and HTTPS for Slack callbacks.
6. Create named credentials in n8n rather than putting tokens into exported workflow JSON.

Important n8n settings to create outside agent code include its encryption key, editor authentication, webhook URL, timezone, and execution data retention policy.

## Step 2: Discovery Workflow

Implement this sequence:

1. Schedule or manual trigger.
2. Load a bounded list of search terms or areas.
3. Call the permitted discovery provider.
4. Normalize and deduplicate domains.
5. Insert or upsert prospects in Postgres.
6. Call the scraper endpoint.
7. Store scraped assets and mark the prospect `SCRAPED`.
8. Call the agent audit endpoint.
9. Record workflow execution ID and errors.

Add rate limits, exponential backoff, per-domain limits, and a dead-letter path for repeated failures.

## Step 3: Slack HITL Workflow

1. Receive Slack interaction payload.
2. Verify signature in the agent service.
3. Forward the event with its original metadata.
4. Return a quick acknowledgment.
5. Update the Slack message to show the current decision.
6. Do not let n8n invent or mutate approval state independently.

## Step 4: Deployment and Outreach Workflow

1. Receive a completion event from the agent.
2. Verify the workflow and approval status.
3. Create a pitch draft from a versioned template.
4. Store the draft and intended recipient in Postgres.
5. Send it to an operator review queue.
6. Add a separate explicit send action.
7. Log provider response, message ID, and unsubscribe handling.

Default to draft-only mode until deliverability, consent, suppression, and legal requirements are understood.

## Step 5: Workflow Operations

For every workflow, define:

- input and output contracts
- timeout and retry behavior
- idempotency key
- error branch
- alert destination
- data retention policy
- manual replay procedure

Export workflow definitions without embedded credentials and keep them under version control.

## Exit Checks

- A dry-run discovery creates one prospect and does not duplicate it on retry.
- Slack approval resumes the correct thread.
- Deployment completion creates one outreach draft.
- No email is sent without the separate operator action.
- Failed executions are visible in n8n and correlated with the prospect ID.
