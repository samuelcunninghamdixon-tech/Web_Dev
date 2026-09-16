import json
from pathlib import Path


WORKFLOW_DIR = Path(__file__).parents[1] / "workflows" / "n8n"


def _nodes(filename: str) -> dict[str, dict]:
    document = json.loads((WORKFLOW_DIR / filename).read_text(encoding="utf-8"))
    assert document["nodes"]
    return {node["id"]: node for node in document["nodes"]}


def test_all_workflows_are_valid_json() -> None:
    for path in WORKFLOW_DIR.glob("*.json"):
        document = json.loads(path.read_text(encoding="utf-8"))
        assert document["name"]
        assert document["connections"]


def test_discovery_maps_current_scraper_and_agent_contracts() -> None:
    nodes = _nodes("01_discovery_workflow.json")
    scrape = nodes["scrape"]
    audit = nodes["audit"]

    assert scrape["parameters"]["url"] == "http://scraper-service:8000/scrape"
    assert scrape["parameters"]["method"] == "POST"
    assert "prospect_id" in scrape["parameters"]["jsonBody"]
    assert "screenshot" in scrape["parameters"]["jsonBody"]
    assert audit["parameters"]["url"] == "http://agent-service:8000/api/audit"
    assert audit["parameters"]["method"] == "POST"
    assert "prospect_id" in audit["parameters"]["jsonBody"]
    assert "X-Idempotency-Key" in str(audit["parameters"]["headerParameters"])


def test_slack_workflow_maps_verified_event_to_agent() -> None:
    node = _nodes("02_slack_hitl_workflow.json")["forwardToAgent"]
    parameters = node["parameters"]

    assert parameters["url"] == "http://agent-service:8000/api/slack-event"
    assert parameters["method"] == "POST"
    for field in ("thread_id", "action_id", "user_id", "channel_id", "message_ts", "event_id"):
        assert field in parameters["jsonBody"]
    assert "X-Slack-Signature" in str(parameters["headerParameters"])


def test_outreach_workflow_verifies_state_and_persists_draft() -> None:
    nodes = _nodes("03_deployment_outreach_workflow.json")
    state = nodes["agentState"]
    persist = nodes["persistProspect"]

    assert state["parameters"]["url"].startswith("http://agent-service:8000/api/state/")
    assert state["parameters"]["method"] == "GET"
    assert persist["parameters"]["table"] == "outreach_drafts"
    assert "DRAFT" in persist["parameters"]["values"]
    assert "postgres" in persist["credentials"]


def test_workflow_credentials_are_references_not_secrets() -> None:
    for path in WORKFLOW_DIR.glob("*.json"):
        text = path.read_text(encoding="utf-8")
        assert "Bearer " not in text
        assert "xoxb-" not in text
        assert "sk-" not in text
