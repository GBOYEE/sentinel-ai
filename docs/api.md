# API Reference

## Webhook Endpoint

`POST /webhook`

GitHub sends pull request events here. Requires valid `X-Hub-Signature-256`.

**Payload:** Standard GitHub webhook payload.

Response: `{"status": "processing"}` (202 Accepted). Review is done asynchronously.

## Health Check

`GET /health` Returns `{"status": "ok", "service": "sentinel-ai"}`

## Root

`GET /` Returns service name and version.

## Internal Functions (for contributors)

- `process_pull_request(owner, repo, pull_number, commit_sha)` — orchestrates review
- `scan_file(code, filename)` — runs all static analyzers
- `review_code_with_llm(diff, filename, context)` — LLM-based review
