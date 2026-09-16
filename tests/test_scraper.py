from pathlib import Path

from fastapi.testclient import TestClient

from services.scraper.app import app, extract_page_data


FIXTURE = Path(__file__).parent / "fixtures" / "scraper_fixture.html"


def test_private_and_metadata_targets_are_blocked() -> None:
    client = TestClient(app)
    assert client.post("/scrape", json={"url": "http://127.0.0.1:8080"}).status_code == 400
    assert client.post("/scrape", json={"url": "http://169.254.169.254/latest/meta-data"}).status_code == 400
    assert client.post("/scrape", json={"url": "file:///etc/passwd"}).status_code == 422


def test_fixture_extracts_metadata_and_contacts() -> None:
    result = extract_page_data(FIXTURE.read_text(encoding="utf-8"), "https://example.test/about")
    assert result["title"] == "Example Studio"
    assert result["meta"]["description"] == "A fixture studio"
    assert result["og_image"].url == "https://example.test/assets/og.png"
    assert result["logo_candidates"][0].url == "https://example.test/assets/logo.svg"
    assert result["favicon_candidates"][0].url == "https://example.test/favicon.ico"
    assert result["contact"].email == "hello@example.test"
    assert result["contact"].phone == "+1 555 123 4567"
    assert result["contact"].address == "1 Main Street, Portland, OR, 97201"
    assert result["contact"].social_links == ["https://www.linkedin.com/company/example"]


def test_fixture_url_returns_normalized_response_without_browser(monkeypatch) -> None:
    async def fake_validate(url):
        return str(url)

    async def fake_runner(request):
        data = extract_page_data(FIXTURE.read_text(encoding="utf-8"), str(request.url))
        return str(request.url), data, {"normalized": ["fixture"]}

    monkeypatch.setattr("services.scraper.app.validate_target", fake_validate)
    monkeypatch.setattr(app.state, "browser_runner", fake_runner)
    response = TestClient(app).post("/scrape", json={"url": "https://example.test"})
    assert response.status_code == 200
    assert response.json()["domain"] == "example.test"
    assert response.json()["contact"]["email"] == "hello@example.test"
