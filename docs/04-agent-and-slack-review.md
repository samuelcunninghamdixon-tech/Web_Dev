# Agent Graph and Slack Human Review

## Goal

Make the agent service durable, resumable, and unable to generate or deploy a site before human approval.

## Step 1: Normalize State

Keep `AgencyState` small and serializable. Define typed models for:

- prospect identity and URL
- scraped assets
- audit report
- design brief
- approval status
- human feedback
- generated code and preview URL
- error and retry metadata

Use explicit status transitions such as `DISCOVERED`, `SCRAPED`, `AUDITED`, `AWAITING_REVIEW`, `REVISION_REQUESTED`, `APPROVED`, `GENERATED`, `DEPLOYED`, and `FAILED`.

## Step 2: Build the Graph

Implement nodes with one responsibility:

1. Load the prospect and assets.
2. Call the vision model with a bounded prompt.
3. Parse and validate the audit JSON.
4. Store the audit and send a Slack review card.
5. Pause until a verified Slack action arrives.
6. Apply feedback to the design brief.
7. Route approved work to code generation.
8. Route revisions back to the brief or audit stage.
9. Stop permanently on rejection.

Do not hide network calls or database writes inside route handlers.

## Step 3: Persistence

Configure `AsyncPostgresSaver` with a real connection pool and run its setup/migrations. Use a stable `thread_id` per prospect workflow. Verify that the checkpoint is written before returning a webhook response.

Add idempotency so a repeated Slack event or n8n retry does not advance a thread twice.

## Step 4: Ollama Client

Implement:

- request timeouts and retry limits
- model selection from settings
- explicit `keep_alive` values when switching models
- image encoding in the format Ollama expects
- response schema validation
- fenced JSON and bounded repair parsing
- redacted request/response logging

A parse failure should produce a visible failed state or review task, not silently invent a score.

## Step 5: Slack Security

1. Verify the Slack signature using the raw request body and timestamp.
2. Reject stale requests.
3. Map action IDs one-to-one to allowed state transitions.
4. Record user ID, channel, message timestamp, action, and feedback.
5. Acknowledge quickly, then process asynchronously when work may be slow.
6. Restrict accepted actions to the configured review channel and known workflow thread.

## Step 6: API Endpoints

Implement and document:

- `POST /api/audit`
- `POST /api/slack-event`
- `GET /api/state/{thread_id}`
- `GET /health`
- `GET /ready`

Use request and response models, authentication for internal endpoints, and consistent error bodies.

## Exit Checks

- Start an audit and confirm a checkpoint exists in Postgres.
- Restart the agent container while paused and query the same state.
- Replay the same Slack approval event and confirm no duplicate transition.
- Submit revision feedback and confirm it appears in the next design brief.
- Confirm rejected or unapproved threads cannot reach code generation.
