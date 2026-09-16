# Local AI Web Agency Pipeline

This repository contains the initial skeleton for a locally hosted AI web agency pipeline built around n8n, LangGraph, Ollama, PostgreSQL, and microservices for scraping and code generation.

## Project Structure

- `services/agent` - LangGraph orchestration service
- `services/scraper` - Website scraping and metadata extraction
- `services/codegen` - HTML generation and validation
- `workflows/n8n` - Workflow definitions for discovery, HITL review, and deployment
- `database` - PostgreSQL schema and migration files
- `config` - Model and prompt configuration
- `tests` - Automated tests

## Implementation Guide

The step-by-step plan is in the [`docs`](docs) directory:

1. [Overall roadmap](docs/00-overall-roadmap.md)
2. [External accounts and keys](docs/01-external-accounts-and-keys.md)
3. [Local environment](docs/02-local-environment.md)
4. [Scraper service](docs/03-scraper-service.md)
5. [Agent and Slack review](docs/04-agent-and-slack-review.md)
6. [Code generation and deployment](docs/05-codegen-and-deployment.md)
7. [n8n workflows and outreach](docs/06-n8n-workflows-and-outreach.md)
8. [Testing, security, and operations](docs/07-testing-security-and-operations.md)
9. [Current scaffold gaps](docs/08-current-scaffold-gaps.md)

## Quick Start

1. Copy `.env.example` to `.env` and adjust values
2. Start the stack with Docker Compose
3. Initialize the database schema
4. Trigger the discovery workflow to begin prospect review

## Notes

This is an initial implementation skeleton based on the master plan. It is intended to be expanded into a full production workflow.
