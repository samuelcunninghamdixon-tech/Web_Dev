from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

REQUIRED_SELECTORS = ("main", "h1", "#services", "#contact")


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def validate_required_content(html_content: str) -> list[str]:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html_content, "html.parser")
    errors = [f"Missing required content: {selector}" for selector in REQUIRED_SELECTORS if not soup.select_one(selector)]
    for image in soup.find_all("img"):
        if not image.get("src") and image.get("alt", "").lower() != "placeholder":
            errors.append("Image is missing a usable source or intentional placeholder.")
    for link in soup.find_all("a"):
        if not link.get("href"):
            errors.append("Link is missing a target.")
    return errors


def validate_generated_page(html_content: str, *, browser_factory: Callable[[], Any] | None = None) -> ValidationResult:
    html_content = html_content.strip()
    if not html_content:
        return ValidationResult(False, ["Generated HTML content is empty."])
    errors = validate_required_content(html_content)
    try:
        if browser_factory is None:
            from playwright.sync_api import sync_playwright
            browser_factory = sync_playwright
        with browser_factory() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.on("pageerror", lambda exc: errors.append(f"Page error: {exc}"))
            page.on("console", lambda msg: errors.append(f"Console: {msg.text}") if msg.type == "error" else None)
            page.on("requestfailed", lambda request: errors.append(f"Request failed: {request.url}: {request.failure}"))
            page.on("response", lambda response: errors.append(f"Resource failed: {response.url} ({response.status})") if response.status >= 400 else None)
            page.set_content(html_content, wait_until="load")
            for width in (375, 1440):
                page.set_viewport_size({"width": width, "height": 900})
                if page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth"):
                    errors.append(f"Horizontal overflow at viewport width {width}.")
            browser.close()
    except Exception as exc:  # pragma: no cover - browser guard
        return ValidationResult(False, [f"Validation failed: {exc}"])
    return ValidationResult(not errors, list(dict.fromkeys(errors)))


def validate_generated_code(html_content: str) -> tuple[bool, str]:
    result = validate_generated_page(html_content)
    return result.valid, "Validation passed." if result.valid else "; ".join(result.errors)
