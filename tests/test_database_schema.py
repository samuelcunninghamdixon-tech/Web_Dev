from pathlib import Path


DATABASE_DIR = Path(__file__).parents[1] / "database"


def test_init_schema_contains_required_extensions_tables_and_indexes() -> None:
    schema = (DATABASE_DIR / "init.sql").read_text(encoding="utf-8")

    for expected in (
        "CREATE EXTENSION IF NOT EXISTS pgcrypto",
        "CREATE TABLE IF NOT EXISTS prospects",
        "CREATE TABLE IF NOT EXISTS workflow_events",
        "CREATE TABLE IF NOT EXISTS outreach_drafts",
        "idx_prospects_status",
        "idx_workflow_events_correlation_id",
        "idx_outreach_drafts_status",
    ):
        assert expected in schema


def test_initial_migration_matches_fresh_install_contract() -> None:
    init_schema = (DATABASE_DIR / "init.sql").read_text(encoding="utf-8")
    migration = (DATABASE_DIR / "migrations" / "001_initial_schema.sql").read_text(encoding="utf-8")

    assert migration == init_schema
