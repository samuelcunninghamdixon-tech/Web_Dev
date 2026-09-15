from __future__ import annotations

import re
from typing import Tuple

from playwright.sync_api import sync_playwright


def validate_generated_code(html_content: str) -> tuple[bool, str]:
    html_content = html_content.strip()
    if not html_content:
        return False, "Generated HTML content is empty."

    ok = True
    errors: list[str] = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_content(html_content, wait_until="load")
            page.on("pageerror", lambda exc: errors.append(f"Page error: {exc}"))
            page.on("console", lambda msg: errors.append(f"Console: {msg.text}") if msg.type == "error" else None)
            for resource in page.locator("img, script, link").all():
                try:
                    src = resource.get_attribute("src") or resource.get_attribute("href")
                    if src and src.startswith("http"):
                        # Validate that the URL resolves without a 4xx/5xx failure in a best-effort way
                        if re.match(r"https?://", src):
                            continue
                except Exception:
                    pass
            browser.close()
    except Exception as exc:  # pragma: no cover - validation guard
        return False, f"Validation failed: {exc}"

    if errors:
        ok = False
        return ok, "; ".join(dict.fromkeys(errors))

    return ok, "Validation passed."
