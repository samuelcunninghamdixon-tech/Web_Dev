# Agent Graph and Discord-First Human Review

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
4. Store the audit and send a review message through the configured transport adapter. Discord is the MVP default.
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

## Step 5: Review Transport Abstraction

Define a shared review adapter interface with operations such as:

- `send_review_request(state) -> message reference`
- `acknowledge_action(event) -> None`
- `update_review_message(state) -> None`
- `verify_interaction(request) -> normalized event`

The internal normalized event must contain `thread_id`, `action`, `user_id`, `channel_id`, `message_id`, and optional feedback. The graph must never depend directly on Discord or Slack payload shapes.

### Discord MVP

1. Verify Discord Ed25519 signatures with `DISCORD_PUBLIC_KEY`.
2. Reject stale or malformed interaction requests.
3. Acknowledge button interactions within Discord's response deadline.
4. Map `approve_audit`, `request_revision`, and `reject_audit` to the existing state transitions.
5. Restrict accepted interactions to `DISCORD_REVIEW_GUILD_ID` and `DISCORD_REVIEW_CHANNEL_ID`.
6. Record Discord user, channel, message, and interaction IDs for replay protection.

### Slack Later Version

1. Verify the Slack signature using the raw request body and timestamp.
2. Reject stale requests.
3. Map action IDs one-to-one to allowed state transitions.
4. Record user ID, channel, message timestamp, action, and feedback.
5. Acknowledge quickly, then process asynchronously when work may be slow.
6. Restrict accepted actions to the configured review channel and known workflow thread.

Select the adapter from `REVIEW_PLATFORM`. Supported values are `discord` for the MVP and `slack` for the later adapter.

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
- Set `REVIEW_PLATFORM=discord` and complete approval, revision, and rejection through Discord.
- Restart the agent container while paused and query the same state.
- Replay the same Slack approval event and confirm no duplicate transition.
- Submit revision feedback and confirm it appears in the next design brief.
- Confirm rejected or unapproved threads cannot reach code generation.
