"""Main FastAPI application for Sentinel AI."""

import os
import json
import logging
from typing import List, Dict, Any
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from config import ENABLE_STATIC_ANALYSIS, ENABLE_LLM_REVIEW
from gh_auth import verify_webhook_signature, create_jwt
from scanners import scan_file
from llm_reviewer import review_code_with_llm
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Sentinel AI", version="0.1.0")


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


class ReviewResult(BaseModel):
    pull_number: int
    findings: List[Finding]
    summary: str


def get_file_content(owner: str, repo: str, path: str, ref: str) -> str:
    """Fetch file content from GitHub API."""
    token = create_jwt()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={ref}"
    resp = httpx.get(url, headers=headers)
    if resp.status_code == 200:
        import base64
        content = base64.b64decode(resp.json()["content"]).decode("utf-8")
        return content
    return ""


def post_review_comment(owner: str, repo: str, pull_number: int, findings: List[Finding]) -> bool:
    """Post review comments on the PR."""
    token = create_jwt()
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/comments"
    body = "## Sentinel AI Review\n\n"
    if not findings:
        body += "✅ No issues found. Great job!"
        payload = {"body": body}
        resp = httpx.post(url, headers=headers, json=payload)
        return resp.status_code == 201

    body += f"Found {len(findings)} issues:\n\n"
    for i, f in enumerate(findings, 1):
        body += f"**{i}. [{f.severity.upper()}] {f.description}** (line {f.line}, {f.category})\n"
        if f.suggestion:
            body += f"\n> Suggestion: {f.suggestion}\n\n"
        body += f"*{f.tool}*\n\n"

    payload = {"body": body}
    resp = httpx.post(url, headers=headers, json=payload)
    if resp.status_code != 201:
        logger.error(f"Failed to post review: {resp.status_code} {resp.text}")
    return resp.status_code == 201


def process_pull_request(owner: str, repo: str, pull_number: int, commit_sha: str):
    """Main review pipeline."""
    logger.info(f"Processing PR #{pull_number} in {owner}/{repo}")

    token = create_jwt()
    headers = {"Authorization": f"Bearer {token}"}
    pr_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/files"
    resp = httpx.get(pr_url, headers=headers)
    if resp.status_code != 200:
        logger.error(f"Failed to get PR files: {resp.status_code}")
        return

    files = resp.json()
    all_findings: List[Finding] = []

    for file_data in files:
        filename = file_data["filename"]
        patch = file_data.get("patch", "")
        if not patch:
            continue

        if filename.endswith(".py") and ENABLE_STATIC_ANALYSIS:
            findings = scan_file(patch, filename)
            for f in findings:
                all_findings.append(Finding(
                    line=f.get("line", 0),
                    severity=f.get("severity", "medium"),
                    category="security" if f["tool"] == "bandit" else "quality",
                    description=f.get("message", ""),
                    suggestion="",
                    tool=f["tool"],
                ))

        if ENABLE_LLM_REVIEW and filename.endswith((".py", ".js", ".ts", ".go", ".rs")):
            context = get_file_content(owner, repo, filename, commit_sha)
            llm_findings = review_code_with_llm(patch, filename, context)
            for f in llm_findings:
                all_findings.append(Finding(
                    line=f.get("line", 0),
                    severity=f.get("severity", "medium"),
                    category=f.get("category", "quality"),
                    description=f.get("description", ""),
                    suggestion=f.get("suggestion", ""),
                    tool="llm",
                ))

    success = post_review_comment(owner, repo, pull_number, all_findings)
    if success:
        logger.info(f"Posted review with {len(all_findings)} findings")
    else:
        logger.error("Failed to post review")


@app.post("/webhook")
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
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

    return JSONResponse({"status": "processing"}, status_code=202)


@app.get("/health")
def health():
    return {"status": "ok", "service": "sentinel-ai"}


@app.get("/")
def root():
    return {"name": "Sentinel AI", "version": "0.1.0", "status": "running"}
