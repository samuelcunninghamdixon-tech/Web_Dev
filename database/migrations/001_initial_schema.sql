CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS prospects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_name VARCHAR(255) NOT NULL,
    website_url TEXT NOT NULL,
    domain VARCHAR(255) UNIQUE NOT NULL,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    tech_stack JSONB NOT NULL DEFAULT '{}'::jsonb,
    scraped_assets JSONB NOT NULL DEFAULT '{}'::jsonb,
    audit_results JSONB NOT NULL DEFAULT '{}'::jsonb,
    status VARCHAR(50) NOT NULL DEFAULT 'DISCOVERED',
    slack_thread_id VARCHAR(100),
    github_preview_url TEXT,
    correlation_id UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS workflow_events (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    event_id VARCHAR(255) NOT NULL,
    idempotency_key VARCHAR(255) NOT NULL UNIQUE,
    correlation_id UUID NOT NULL,
    prospect_id UUID REFERENCES prospects(id) ON DELETE SET NULL,
    thread_id VARCHAR(200),
    event_type VARCHAR(100) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'RECEIVED',
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS outreach_drafts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prospect_id UUID NOT NULL REFERENCES prospects(id) ON DELETE CASCADE,
    correlation_id UUID NOT NULL,
    recipient_email VARCHAR(255) NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'DRAFT',
    provider_message_id VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (prospect_id, correlation_id)
);

CREATE INDEX IF NOT EXISTS idx_prospects_status ON prospects(status);
CREATE INDEX IF NOT EXISTS idx_prospects_correlation_id ON prospects(correlation_id);
CREATE INDEX IF NOT EXISTS idx_workflow_events_correlation_id ON workflow_events(correlation_id);
CREATE INDEX IF NOT EXISTS idx_workflow_events_prospect_id ON workflow_events(prospect_id);
CREATE INDEX IF NOT EXISTS idx_workflow_events_created_at ON workflow_events(created_at);
CREATE INDEX IF NOT EXISTS idx_outreach_drafts_status ON outreach_drafts(status);
