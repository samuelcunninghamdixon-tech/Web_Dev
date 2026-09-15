CREATE TABLE IF NOT EXISTS prospects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_name VARCHAR(255) NOT NULL,
    website_url TEXT NOT NULL,
    domain VARCHAR(255) UNIQUE NOT NULL,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    tech_stack JSONB DEFAULT '{}'::jsonb,
    scraped_assets JSONB DEFAULT '{}'::jsonb,
    audit_results JSONB DEFAULT '{}'::jsonb,
    status VARCHAR(50) DEFAULT 'DISCOVERED',
    slack_thread_id VARCHAR(100),
    github_preview_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_prospects_domain ON prospects(domain);
CREATE INDEX IF NOT EXISTS idx_prospects_status ON prospects(status);
