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

## Quick Start

1. Copy `.env.example` to `.env` and adjust values
2. Start the stack with Docker Compose
3. Initialize the database schema
4. Trigger the discovery workflow to begin prospect review

## Notes

This is an initial implementation skeleton based on the master plan. It is intended to be expanded into a full production workflow.
