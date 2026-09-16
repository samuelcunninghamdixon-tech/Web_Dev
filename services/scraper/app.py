from __future__ import annotations

import asyncio
import ipaddress
import json
import os
import re
import socket
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse
from uuid import uuid4

from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


MAX_PAGE_TIMEOUT_SECONDS = 30
SOCIAL_HOSTS = {
    "facebook.com", "instagram.com", "linkedin.com", "pinterest.com",
    "tiktok.com", "twitter.com", "x.com", "youtube.com",
}
EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE_PATTERN = re.compile(r"(?<!\w)(?:\+?\d[\d(). -]{7,}\d)(?!\w)")


class ScreenshotPreferences(BaseModel):
    enabled: bool = True
    full_page: bool = True


class ScrapeRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    url: HttpUrl
    prospect_id: str | None = Field(default=None, max_length=200)
    screenshot: ScreenshotPreferences = Field(default_factory=ScreenshotPreferences)

    @field_validator("url")
    @classmethod
    def require_http_url(cls, value: HttpUrl) -> HttpUrl:
        if value.scheme not in {"http", "https"}:
            raise ValueError("url must use http or https")
        return value


class Candidate(BaseModel):
    url: str
    source: str
    confidence: float = Field(ge=0, le=1)


class ContactData(BaseModel):
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    social_links: list[str] = Field(default_factory=list)


class TechnologyData(BaseModel):
    normalized: list[str] = Field(default_factory=list)
    raw: dict[str, Any] | None = None


class ScrapeResponse(BaseModel):
    url: str
    domain: str
    title: str | None = None
    meta: dict[str, str] = Field(default_factory=dict)
    screenshot_path: str | None = None
    logo_candidates: list[Candidate] = Field(default_factory=list)
    favicon_candidates: list[Candidate] = Field(default_factory=list)
    og_image: Candidate | None = None
    primary_color: str | None = None
    secondary_color: str | None = None
    contact: ContactData = Field(default_factory=ContactData)
    technology: TechnologyData = Field(default_factory=TechnologyData)
    warnings: list[str] = Field(default_factory=list)
    extraction_errors: list[str] = Field(default_factory=list)
    started_at: datetime
    completed_at: datetime
    duration_ms: int


class ScrapeFailure(Exception):
    def __init__(self, message: str, *, timeout: bool = False) -> None:
        super().__init__(message)
        self.timeout = timeout


def _host_is_blocked(hostname: str) -> bool:
    normalized = hostname.rstrip(".").lower()
    if normalized in {"localhost", "localhost.localdomain", "metadata.google.internal"}:
        return True
    try:
        address = ipaddress.ip_address(normalized)
    except ValueError:
        return False
    return (
        address.is_private or address.is_loopback or address.is_link_local
        or address.is_reserved or address.is_unspecified
        or str(address) in {"169.254.169.254", "100.100.100.200"}
    )


async def validate_target(url: str | HttpUrl) -> str:
    parsed = urlparse(str(url))
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise HTTPException(status_code=422, detail="url must be an http or https URL")
    hostname = parsed.hostname
    if _host_is_blocked(hostname):
        raise HTTPException(status_code=400, detail="target host is blocked")
    try:
        addresses = await asyncio.to_thread(
            socket.getaddrinfo,
            hostname,
            parsed.port or (443 if parsed.scheme == "https" else 80),
            type=socket.SOCK_STREAM,
        )
    except socket.gaierror as error:
        raise HTTPException(status_code=400, detail="target host could not be resolved") from error
    if any(_host_is_blocked(item[4][0]) for item in addresses):
        raise HTTPException(status_code=400, detail="target resolves to a blocked network")
    return parsed.geturl()


def _absolute_url(value: str, page_url: str) -> str:
    return urljoin(page_url, value.strip())


def _candidate(value: str | None, page_url: str, source: str, confidence: float) -> Candidate | None:
    if not value or value.startswith("data:"):
        return None
    return Candidate(url=_absolute_url(value, page_url), source=source, confidence=confidence)


def _jsonld_contacts(value: Any) -> tuple[str | None, str | None, str | None]:
    if isinstance(value, list):
        for item in value:
            result = _jsonld_contacts(item)
            if any(result):
                return result
        return None, None, None
    if not isinstance(value, dict):
        return None, None, None
    for nested in (value.get("@graph"), value.get("mainEntity"), value.get("publisher"), value.get("organization")):
        result = _jsonld_contacts(nested)
        if any(result):
            return result
    if value.get("@type") in {"Organization", "LocalBusiness", "Person", "Corporation"} or any(
        key in value for key in ("email", "telephone", "address")
    ):
        address = value.get("address")
        if isinstance(address, dict):
            address = ", ".join(str(address[key]) for key in ("streetAddress", "addressLocality", "addressRegion", "postalCode") if address.get(key))
        return value.get("email"), value.get("telephone"), address if isinstance(address, str) else None
    return None, None, None


def extract_page_data(html: str, page_url: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    warnings: list[str] = []
    meta: dict[str, str] = {}
    for tag in soup.find_all("meta"):
        key = tag.get("name") or tag.get("property")
        content = tag.get("content")
        if key and content:
            meta[str(key)] = str(content).strip()
    logo_candidates: list[Candidate] = []
    favicon_candidates: list[Candidate] = []
    for image in soup.find_all(["img", "svg"]):
        attributes = " ".join(str(image.get(key, "")) for key in ("id", "class", "alt", "aria-label")).lower()
        if "logo" in attributes:
            source = image.get("src") or image.get("data-src") or image.get("href")
            item = _candidate(source, page_url, "logo attribute", 0.95)
            if item:
                logo_candidates.append(item)
    for link in soup.find_all("link", href=True):
        rel = {str(item).lower() for item in link.get("rel", [])}
        if rel & {"icon", "shortcut icon", "apple-touch-icon"}:
            item = _candidate(link["href"], page_url, "favicon link", 1.0)
            if item:
                favicon_candidates.append(item)
        if "logo" in str(link.get("href", "")).lower():
            item = _candidate(link["href"], page_url, "logo link", 0.7)
            if item:
                logo_candidates.append(item)
    og_value = soup.find("meta", attrs={"property": "og:image"})
    og_image = _candidate(og_value.get("content") if og_value else None, page_url, "og:image", 1.0)
    colors: list[str] = []
    for tag in soup.find_all(["header", "button", "a", "section", "nav"]):
        style = str(tag.get("style", ""))
        colors.extend(re.findall(r"(?:color|background-color)\s*:\s*(#[0-9a-fA-F]{3,8}|rgb\([^)]*\))", style, re.I))
    if not colors:
        warnings.append("no inline CSS colors found")

    email: str | None = None
    phone: str | None = None
    address: str | None = None
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            jsonld = json.loads(script.string or script.get_text())
        except (TypeError, json.JSONDecodeError):
            warnings.append("malformed JSON-LD ignored")
            continue
        email, phone, address = _jsonld_contacts(jsonld)
        if email or phone or address:
            break
    visible_text = soup.get_text(" ", strip=True)
    email_match = EMAIL_PATTERN.search(visible_text)
    phone_match = PHONE_PATTERN.search(visible_text)
    email = email or (email_match.group(0) if email_match else None)
    phone = phone or (phone_match.group(0) if phone_match else None)
    social_links: list[str] = []
    for anchor in soup.find_all("a", href=True):
        link_url = _absolute_url(anchor["href"], page_url)
        host = urlparse(link_url).hostname or ""
        if any(host == social_host or host.endswith("." + social_host) for social_host in SOCIAL_HOSTS):
            if link_url not in social_links:
                social_links.append(link_url)
    return {
        "title": soup.title.get_text(strip=True) if soup.title else None,
        "meta": meta,
        "logo_candidates": logo_candidates,
        "favicon_candidates": favicon_candidates,
        "og_image": og_image,
        "primary_color": colors[0] if colors else None,
        "secondary_color": colors[1] if len(colors) > 1 else None,
        "contact": ContactData(email=email, phone=phone, address=address, social_links=social_links),
        "warnings": warnings,
        "extraction_errors": [],
    }


async def detect_technology(url: str) -> TechnologyData:
    try:
        from wappalyzer import Wappalyzer, WebPage  # type: ignore[import-not-found]
        result = await asyncio.to_thread(lambda: Wappalyzer.latest().analyze(WebPage.new_from_url(url)))
        return TechnologyData(normalized=sorted(str(item) for item in result), raw={"detected": sorted(result)})
    except Exception:
        return TechnologyData()


async def scrape_with_browser(request: ScrapeRequest) -> tuple[str, dict[str, Any], TechnologyData]:
    from playwright.async_api import TimeoutError as PlaywrightTimeoutError, async_playwright
    target = await validate_target(request.url)
    root = Path(os.getenv("SHARED_ROOT", "/shared"))
    screenshot_dir = root / "screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    parsed = urlparse(target)
    screenshot_path = screenshot_dir / f"{re.sub(r'[^a-zA-Z0-9.-]', '-', parsed.hostname or 'site')}-{uuid4().hex}.png"
    browser = context = page = None
    try:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            page.set_default_timeout(MAX_PAGE_TIMEOUT_SECONDS * 1000)
            await page.goto(target, wait_until="domcontentloaded", timeout=MAX_PAGE_TIMEOUT_SECONDS * 1000)
            try:
                await page.wait_for_load_state("networkidle", timeout=5000)
            except PlaywrightTimeoutError:
                pass
            html = await page.content()
            if request.screenshot.enabled:
                await page.screenshot(path=str(screenshot_path), full_page=request.screenshot.full_page)
            else:
                screenshot_path = None
            data = extract_page_data(html, target)
            data["screenshot_path"] = str(screenshot_path) if screenshot_path else None
            return target, data, await detect_technology(target)
    except PlaywrightTimeoutError as error:
        raise ScrapeFailure("page load exceeded 30 seconds", timeout=True) from error
    except Exception as error:
        raise ScrapeFailure(str(error)) from error
    finally:
        try:
            if page:
                await page.close()
        finally:
            try:
                if context:
                    await context.close()
            finally:
                if browser:
                    await browser.close()

app = FastAPI(title="Scraper Service")
app.state.browser_runner = scrape_with_browser


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@app.get("/ready")
def readiness_check() -> dict:
    return {"status": "ready", "checks": {"configuration": "ok"}}


@app.post("/scrape", response_model=ScrapeResponse)
async def scrape(request: ScrapeRequest) -> ScrapeResponse:
    started = datetime.now(timezone.utc)
    start_time = time.monotonic()
    target = await validate_target(request.url)
    try:
        target, extracted, technology = await app.state.browser_runner(request)
    except ScrapeFailure as error:
        status = 504 if error.timeout else 502
        raise HTTPException(status_code=status, detail=str(error)) from error
    completed = datetime.now(timezone.utc)
    parsed = urlparse(target)
    return ScrapeResponse(
        url=target,
        domain=parsed.hostname or "",
        screenshot_path=extracted.pop("screenshot_path", None),
        technology=technology,
        started_at=started,
        completed_at=completed,
        duration_ms=round((time.monotonic() - start_time) * 1000),
        **extracted,
    )
