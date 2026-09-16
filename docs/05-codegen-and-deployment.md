# Code Generation, Validation, and Preview Deployment

## Goal

Generate a usable, brand-aware single-page site from approved data, validate it in a browser, and deploy only approved output.

## Step 1: Define the Generator Contract

Inputs:

- validated design brief
- normalized asset record
- approved content fields
- allowed external links

Outputs:

- HTML content
- generation metadata
- model name and prompt version
- warnings

Keep prompts and output constraints versioned in `config`. Require the model to return only the intended HTML document.

## Step 2: Enforce Content and Security Boundaries

1. Escape inserted text and attributes.
2. Allow only approved asset and external URLs.
3. Remove scripts that are not on an allowlist.
4. Prevent generated code from accessing internal services or secrets.
5. Keep forms non-functional or route them to an explicitly configured destination until a backend exists.
6. Do not place API keys, tokens, or private source data into generated HTML.

## Step 3: Browser Validation

Use Playwright to load the generated document in an isolated context and check:

- the document loads without page errors
- required sections and headings exist
- images have usable sources or intentional placeholders
- external resources do not return obvious failures
- the page has no horizontal overflow at mobile and desktop widths
- primary links and buttons have valid targets
- console errors are collected

Return machine-readable errors for a bounded repair loop. Stop after a small number of attempts and send the result to human review.

## Step 4: GitHub Pages Deployment

1. Validate the final HTML again after repair.
2. Require approval status `approved`.
3. Create or update `index.html` through the GitHub Contents API.
4. Handle an existing file SHA when updating.
5. Record commit SHA, repository, branch, and preview URL.
6. Poll or verify Pages availability before reporting success.
7. Never deploy from arbitrary user-provided repository names without allowlisting.

## Step 5: Preview Review

Send the preview URL back to Slack. Add a second optional approval gate for publishing or outreach. Keep generated artifacts tied to the prospect and workflow thread.

## Step 6: Tests

Add tests for HTML generation with representative briefs, unsafe text escaping, empty assets, JSON/model failures, validation errors, repair limits, GitHub API responses, existing-file updates, and missing credentials.

## Exit Checks

- Approved data produces a complete HTML document.
- Invalid model output is rejected or repaired within the attempt limit.
- Browser validation catches a deliberate broken resource or missing required section.
- Deployment is skipped without credentials and cannot run for an unapproved thread.
- The recorded preview URL maps to the committed artifact.
