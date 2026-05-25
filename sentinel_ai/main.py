"""Main FastAPI application for Sentinel AI."""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from sentinel_ai.config import ENABLE_STATIC_ANALYSIS, ENABLE_LLM_REVIEW
from sentinel_ai.gh_auth import verify_webhook_signature, get_installation_id, get_installation_token
from sentinel_ai.scanners import scan_file
from sentinel_ai.llm_reviewer import review_code_with_llm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Sentinel AI", version="0.1.0")

# ── Data Models ──────────────────────────────────────────────

class PRReviewRequest(BaseModel):
    owner: str
    repo: str
    pull_number: int
    diff_url: str
    commit_sha: str

class Finding(BaseModel):
    line: int
    severity: str
    category: str
    description: str
    suggestion: str
    tool: str
    filename: str = ""

class ReviewResult(BaseModel):
    pull_number: int
    findings: List[Finding]
    summary: str


# ── GitHub API Helpers ───────────────────────────────────────

async def github_request(method: str, url: str, token: str, data: Optional[dict] = None) -> Optional[Any]:
    """Make an authenticated GitHub API request."""
    import httpx
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    async with httpx.AsyncClient(timeout=30) as client:
        if method == "GET":
            resp = await client.get(url, headers=headers)
        elif method == "POST":
            resp = await client.post(url, headers=headers, json=data)
        else:
            return None
        
        if resp.status_code in (200, 201):
            return resp.json()
        else:
            logger.error(f"GitHub API error: {resp.status_code} {resp.text}")
            return None


async def get_pr_files(owner: str, repo: str, pull_number: int, token: str) -> List[Dict[str, Any]]:
    """Get list of files changed in a PR."""
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/files"
    result = await github_request("GET", url, token)
    if isinstance(result, list):
        return result
    return []


async def get_file_content(owner: str, repo: str, path: str, ref: str, token: str) -> str:
    """Fetch file content from GitHub API."""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={ref}"
    result = await github_request("GET", url, token)
    if result and "content" in result:
        import base64
        return base64.b64decode(result["content"]).decode("utf-8", errors="ignore")
    return ""


async def post_review(
    owner: str, repo: str, pull_number: int,
    commit_sha: str, findings: List[Finding], token: str
) -> bool:
    """Post inline review comments using GitHub Review API.
    
    This is the proper way to review PRs — each finding gets an inline
    comment on the specific line, not a single summary comment.
    """
    if not findings:
        # Post a clean review with no comments
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/reviews"
        data = {
            "commit_id": commit_sha,
            "body": "✅ **Sentinel AI Review** — No issues found. Clean code!",
            "event": "APPROVE",
        }
        result = await github_request("POST", url, token, data)
        return result is not None

    # Group findings by filename
    by_file: Dict[str, List[Finding]] = {}
    for f in findings:
        by_file.setdefault(f.filename, []).append(f)

    # Build review comments
    comments = []
    for filename, file_findings in by_file.items():
        for f in file_findings:
            # Only comment on lines that exist in the diff
            if f.line > 0:
                comment_body = f"**[{f.severity.upper()}] {f.category}** ({f.tool})\n\n{f.description}"
                if f.suggestion:
                    comment_body += f"\n\n💡 **Suggestion:** {f.suggestion}"
                comments.append({
                    "path": filename,
                    "line": f.line,
                    "body": comment_body,
                    "side": "RIGHT",
                })

    # Determine overall event
    severities = [f.severity for f in findings]
    if "critical" in severities or "high" in severities:
        event = "REQUEST_CHANGES"
        summary = f"🚨 **Sentinel AI found {len(findings)} issues** — requires changes"
    elif "medium" in severities:
        event = "COMMENT"
        summary = f"⚠️ **Sentinel AI found {len(findings)} issues** — review recommended"
    else:
        event = "COMMENT"
        summary = f"ℹ️ **Sentinel AI found {len(findings)} minor issues**"

    # Build summary body
    body_lines = [summary, ""]
    for f in findings:
        body_lines.append(f"- **[{f.severity.upper()}]** `{f.filename}:{f.line}` — {f.description} ({f.tool})")

    # Post the review (max 50 comments per review)
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/reviews"
    data = {
        "commit_id": commit_sha,
        "body": "\n".join(body_lines),
        "event": event,
        "comments": comments[:50],  # GitHub limit
    }
    result = await github_request("POST", url, token, data)
    if result:
        logger.info(f"Posted review with {len(comments)} inline comments on PR #{pull_number}")
        return True
    else:
        logger.error(f"Failed to post review on PR #{pull_number}")
        return False


# ── Core Review Pipeline ─────────────────────────────────────

async def process_pull_request(owner: str, repo: str, pull_number: int, commit_sha: str):
    """Main review pipeline: scan → analyze → post review."""
    logger.info(f"Processing PR #{pull_number} in {owner}/{repo}")

    # Get installation token
    installation_id = await get_installation_id(owner, repo)
    if not installation_id:
        logger.error(f"No installation found for {owner}/{repo}")
        return

    token = await get_installation_token(installation_id)
    if not token:
        logger.error(f"Failed to get installation token for {owner}/{repo}")
        return

    # Get PR files
    files = await get_pr_files(owner, repo, pull_number, token)
    if not files:
        logger.warning(f"No files found in PR #{pull_number}")
        return

    all_findings: List[Finding] = []

    for file_data in files:
        filename = file_data["filename"]
        patch = file_data.get("patch", "")
        if not patch:
            continue

        # Static analysis (Python only for now)
        if filename.endswith(".py") and ENABLE_STATIC_ANALYSIS:
            try:
                scan_results = scan_file(patch, filename)
                for sr in scan_results:
                    all_findings.append(Finding(
                        line=sr.get("line", 0),
                        severity=sr.get("severity", "medium"),
                        category="security" if sr["tool"] == "bandit" else "quality",
                        description=sr.get("message", ""),
                        suggestion=sr.get("remediation", ""),
                        tool=sr["tool"],
                        filename=filename,
                    ))
            except Exception as e:
                logger.error(f"Static analysis error on {filename}: {e}")

        # LLM review (all supported languages)
        if ENABLE_LLM_REVIEW and filename.endswith((".py", ".js", ".ts", ".go", ".rs", ".java", ".rb")):
            try:
                context = await get_file_content(owner, repo, filename, commit_sha, token)
                llm_results = await review_code_with_llm(patch, filename, context)
                for lr in llm_results:
                    all_findings.append(Finding(
                        line=lr.get("line", 0),
                        severity=lr.get("severity", "medium"),
                        category=lr.get("category", "quality"),
                        description=lr.get("description", ""),
                        suggestion=lr.get("suggestion", ""),
                        tool="llm",
                        filename=filename,
                    ))
            except Exception as e:
                logger.error(f"LLM review error on {filename}: {e}")

    # Post the review
    success = await post_review(owner, repo, pull_number, commit_sha, all_findings, token)
    if success:
        logger.info(f"✅ Review complete for PR #{pull_number}: {len(all_findings)} findings")
    else:
        logger.error(f"❌ Failed to post review for PR #{pull_number}")


# ── API Endpoints ────────────────────────────────────────────

@app.post("/webhook")
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    """Handle GitHub webhook events."""
    signature = request.headers.get("X-Hub-Signature-256", "")
    body = await request.body()
    
    if not verify_webhook_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = json.loads(body)
    event = request.headers.get("X-GitHub-Event", "")

    if event == "pull_request" and payload.get("action") in ["opened", "synchronize"]:
        pr = payload["pull_request"]
        owner = payload["repository"]["owner"]["login"]
        repo = payload["repository"]["name"]
        pull_number = pr["number"]
        commit_sha = pr["head"]["sha"]

        background_tasks.add_task(process_pull_request, owner, repo, pull_number, commit_sha)
        logger.info(f"Queued review for PR #{pull_number} in {owner}/{repo}")

    elif event == "installation" and payload.get("action") == "created":
        logger.info(f"App installed on {payload.get('repositories', [])}")

    elif event == "installation_repositories":
        logger.info(f"Repos added to installation: {payload.get('repositories_added', [])}")

    return JSONResponse({"status": "processing"}, status_code=202)


@app.get("/health")
def health():
    return {"status": "ok", "service": "sentinel-ai", "version": "0.1.0"}


@app.get("/")
def root():
    return {"name": "Sentinel AI", "version": "0.1.0", "status": "running"}


@app.post("/review")
async def manual_review(request: PRReviewRequest):
    """Manual review endpoint (for testing without webhook)."""
    background_tasks = BackgroundTasks()
    background_tasks.add_task(
        process_pull_request,
        request.owner, request.repo, request.pull_number, request.commit_sha
    )
    return {"status": "queued", "pull_number": request.pull_number}
