# 🛡️ Sentinel AI — GitHub Marketplace Listing Prep
# Ready to submit at: https://github.com/marketplace/new

## Listing Details

- **Name:** Sentinel AI
- **Short description (100 chars):** AI-powered automated code review for GitHub. Catches security bugs, quality issues, and bad practices on every PR.
- **Full description:**
  Sentinel AI is an AI-powered code review bot that automatically reviews every pull request on your repositories. It combines static analysis tools (bandit, flake8, semgrep) with LLM reasoning to catch:

  🔴 Security vulnerabilities: SQL injection, XSS, command injection, hardcoded secrets, eval misuse, path traversal, SSRF
  🟡 Code quality issues: Complexity, duplication, anti-patterns, naming conventions
  🟢 Best practices: Error handling, input validation, secure defaults

  Reviews appear as inline comments on specific lines of your PR — not a wall of text. Critical issues request changes. Medium/low are advisory.

  Built with Python + FastAPI. Open source (MIT). FastAPI webhook server with GitHub App integration.

- **Category:** Code Quality > Code Security
- **URL:** https://gboyee.github.io/sentinel-ai/
- **Logo URL:** (upload sentinel-ai-logo.png or use shield emoji 🛡️)
- **Screenshots:** Upload from /root/github-dev/projects/sentinel-ai/screenshots/

## Pricing Plans

### Free — $0/mo
- Static analysis (bandit) only
- Up to 5 repos
- Python only
- Inline PR comments

### Pro — $9/repo/mo
- Everything in Free
- AI-powered LLM review (all languages)
- Unlimited repos
- Review dashboard
- Priority processing
- 50+ vulnerability patterns

### Team — $29/repo/mo
- Everything in Pro
- Custom review rules
- Slack notifications
- SAML SSO
- Priority support
- Audit logs

## Submission Steps

1. Go to https://github.com/settings/apps/sentinel-ai
2. Scroll to "Marketplace" section
3. Click "List in Marketplace" or continue existing draft
4. Fill in details above
5. Set pricing plans
6. Upload screenshots (see screenshots/ folder)
7. Click "Submit for review"
8. GitHub reviews in 1-3 business days

## Screenshots Needed
- [ ] Bot reviewing a PR (show inline comments with severity)
- [ ] Dashboard showing findings
- [ ] Installation/setup flow
- [ ] Before/after: bug caught by sentinel-ai

## After Approval - Marketing Checklist
- [ ] Tweet/X: Screenshot of bot reviewing PR + link
- [ ] Hacker News: "Show HN: Sentinel AI — free AI code review for GitHub"
- [ ] Reddit: r/programming, r/github, r/codereview, r/cybersecurity
- [ ] Dev.to: Short post about building it
- [ ] Badge on repos: [![Sentinel AI](https://img.shields.io/badge/reviewed%20by-sentinel--ai-6365f1)](https://github.com/marketplace/sentinel-ai)
