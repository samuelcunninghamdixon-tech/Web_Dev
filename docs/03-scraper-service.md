# Scraper Service Implementation

## Goal

Turn `services/scraper` into a bounded, testable service that accepts a URL and returns a normalized prospect asset record.

## Step 1: Define the API Contract

Implement `POST /scrape` with a request model containing:

- `url`
- optional `prospect_id`
- optional screenshot preferences

Return a response model containing:

- normalized URL and domain
- screenshot path
- logo and favicon candidates
- `og:image`
- primary and secondary colors
- contact email, phone, address, and social links
- detected technology stack
- warnings and extraction errors
- timestamps and duration

Return structured 4xx errors for invalid URLs and 5xx errors only for service failures.

## Step 2: Browser Lifecycle

1. Validate `http` and `https` URLs.
2. Create one Playwright browser context per request or controlled worker.
3. Set a total page timeout of 30 seconds.
4. Wait for a useful load state without waiting forever for analytics or ads.
5. Capture a full-page screenshot under a sanitized domain-based filename.
6. Always close the page, context, and browser in `finally` blocks.
7. Prevent access to localhost, private IP ranges, cloud metadata endpoints, and file URLs to reduce SSRF risk.

## Step 3: Asset and Metadata Extraction

Implement independent extractors for:

- SVG and raster logos
- favicon links
- Open Graph metadata
- CSS colors from headers, buttons, links, and hero elements
- schema.org JSON-LD
- visible contact text using conservative regex fallbacks
- social profile links

Preserve source URLs and confidence values so an operator can tell whether a value was explicit or inferred.

## Step 4: Technology Detection

Integrate Wappalyzer or a maintained equivalent behind an adapter. Store the raw detector response separately from normalized values such as CMS, hosting, analytics, booking, payments, and marketing tools.

## Step 5: Storage and Cleanup

Write screenshots and raw extraction artifacts below the configured shared root. Apply file size limits, safe filenames, retention rules, and a cleanup job. Store only paths and metadata in Postgres.

## Step 6: Tests

Add tests for URL validation, private-network blocking, timeout behavior, browser cleanup, JSON-LD extraction, regex fallback, color normalization, and a fixture page. Use a local fixture instead of depending on a live website in unit tests.

## Exit Checks

- A valid fixture URL returns the expected normalized fields.
- A slow page returns a bounded timeout error.
- A page with malformed metadata still returns partial results and warnings.
- No browser process remains after success or failure.
- The endpoint is not reachable from outside the intended network in production.
