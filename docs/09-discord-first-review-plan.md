# Discord-First Review Plan

## MVP Decision

Discord is the primary human-review transport for the first usable release. Slack remains a future adapter selected through `REVIEW_PLATFORM` and does not influence the graph's internal state model.

## MVP Interaction

```text
Agent audit completes
  -> Discord embed with audit summary
  -> Approve / Request Revision / Reject buttons
  -> Discord signature verification
  -> immediate interaction acknowledgment
  -> normalized review event
  -> existing LangGraph state transition
```

## Implementation Order

1. Add `REVIEW_PLATFORM` and Discord settings validation.
2. Create a `ReviewTransport` protocol.
3. Move the current Slack event normalization behind that protocol.
4. Add Discord Ed25519 verification and interaction parsing.
5. Add Discord message publishing and message-update helpers.
6. Replace direct Slack calls in the audit node with the selected transport.
7. Add Discord tests for valid signatures, stale requests, invalid channels, button mapping, and duplicate interaction IDs.
8. Run an end-to-end Discord review against a test server.
9. Add Slack as a second adapter only after the Discord path is stable.

## Environment Selection

Use `REVIEW_PLATFORM=discord` for the MVP. The service should fail startup if Discord is selected and the required Discord settings are missing. Slack settings should not be required unless `REVIEW_PLATFORM=slack`.

## Shared Contract

Both adapters must produce the same internal event:

```json
{
  "thread_id": "workflow-thread-id",
  "action": "approve",
  "user_id": "platform-user-id",
  "channel_id": "review-channel-id",
  "message_id": "platform-message-id",
  "interaction_id": "unique-event-id",
  "feedback": ""
}
```

The graph, persistence, approval gate, code generation, and deployment code should only consume this normalized contract.

## Later Slack Version

The Slack adapter should implement the same `ReviewTransport` protocol and reuse the same action IDs and state transitions. It should add Slack HMAC verification, Block Kit rendering, and Slack thread/message references without changing the graph or database schema.