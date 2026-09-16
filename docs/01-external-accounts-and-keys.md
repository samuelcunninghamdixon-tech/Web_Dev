# External Accounts, Keys, and Human Setup

These items must be created or configured by the operator outside the coding agents. Keep secrets in `.env`, Docker secrets, or a password manager. Never commit them.

## Required Accounts

| Service | Why it is needed | What to create |
| --- | --- | --- |
| Discord | MVP human design review and approval events | A Discord application, bot, private review channel, bot token, public key, and interaction endpoint |
| Slack | Future human review adapter | A Slack workspace, app, webhook, and Interactivity Request URL |
| GitHub | Preview hosting | A repository for generated `index.html` and a token with the smallest required repository/content permissions |
| SMTP or Resend | Outreach drafts or later email delivery | An approved sending domain, sender identity, and API/SMTP credential |
| Prospect source | Business discovery | A permitted Google Maps API, SearXNG instance, or another compliant source |

## Discord Setup (MVP)

1. Create a Discord application in the Discord Developer Portal.
2. Create a bot user and record `DISCORD_BOT_TOKEN`.
3. Record the application ID as `DISCORD_APPLICATION_ID`.
4. Record the application public key as `DISCORD_PUBLIC_KEY`.
5. Create a private review channel and record `DISCORD_REVIEW_CHANNEL_ID`.
6. Record the server ID as `DISCORD_REVIEW_GUILD_ID`.
7. Add the bot to the server with only the permissions needed to send messages, embed links, and use buttons.
8. Register the interaction endpoint at `DISCORD_INTERACTION_URL`.
9. Configure the bot to post an embed with `approve_audit`, `request_revision`, and `reject_audit` button custom IDs.

Discord interaction requests use Ed25519 signatures and must be acknowledged quickly. The endpoint should verify the signature, immediately acknowledge the interaction, and process the workflow asynchronously.

For local-only development, expose the interaction endpoint through a temporary HTTPS tunnel. Do not expose the agent service directly to the public internet.

## Slack Setup (Future Adapter)

1. Create a Slack app in the target workspace.
2. Enable Interactivity and set its request URL to the public n8n webhook for Slack events.
3. Create an incoming webhook for audit messages.
4. Record `SLACK_WEBHOOK_URL`.
5. Record the app `SLACK_SIGNING_SECRET`.
6. Decide whether the service will post to one review channel or create a thread per prospect.
7. Restrict the Slack app to the minimum channels and scopes required.

## GitHub Setup

1. Create a dedicated repository for previews, preferably separate from source code.
2. Enable GitHub Pages from the intended branch and folder.
3. Create a fine-grained token limited to that repository and contents read/write.
4. Record `GITHUB_TOKEN`, `GITHUB_OWNER`, and `GITHUB_REPO`.
5. Confirm the expected URL pattern, for example `https://OWNER.github.io/REPO/`.

## Email Setup

1. Choose Resend or an SMTP provider.
2. Verify the sending domain and configure SPF, DKIM, and DMARC.
3. Create a sender address such as `hello@your-domain.example`.
4. Record the provider key or `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, and `SMTP_PASSWORD`.
5. Start in draft-only mode. Add sending only after legal, consent, unsubscribe, and provider policy requirements are reviewed.

## Prospect Discovery Setup

Choose one permitted source and record its endpoint and credentials if applicable. Add these later as explicit settings such as `DISCOVERY_PROVIDER`, `DISCOVERY_API_URL`, and `DISCOVERY_API_KEY` rather than embedding them in workflow JSON.

Respect provider terms, robots directives where applicable, rate limits, privacy rules, and applicable outreach laws.

## No-Key Local Components

Ollama, Postgres, Docker, and Playwright do not require third-party API keys for the local baseline. They do require disk space, memory, and a compatible browser/runtime. The 32B coder model may require a capable GPU or a slower CPU fallback.

## Secret Checklist

Before starting the stack, verify that `.env` contains real values for database credentials, Ollama endpoints, Discord credentials, GitHub deployment values, and email settings. Slack values are only required when `REVIEW_PLATFORM=slack`. Verify that `.env` is ignored by git and that no secret appears in workflow JSON, logs, screenshots, or generated HTML.
