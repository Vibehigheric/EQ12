#!/usr/bin/env python3
"""
EQ12 Compliance Bot - GitHub App Server
========================================
FastAPI webhook server for GitHub App integration with EQ12 GODSTACK governance.

Features:
- Handles GitHub webhooks (PR events, workflow runs, secret alerts)
- Enforces compliance rules for sensitive business stacks
- Integrates with GitHub REST/GraphQL APIs
- Forwards events to alert_manager.py for monitoring
- Extends Copilot with governance context
"""

import hashlib
import hmac
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import jwt
import requests
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
GITHUB_APP_ID = os.getenv("GITHUB_APP_ID")
GITHUB_PRIVATE_KEY_PATH = os.getenv("GITHUB_PRIVATE_KEY_PATH", "./github-app-private-key.pem")
GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")
ALERT_MANAGER_URL = os.getenv("ALERT_MANAGER_URL", "http://localhost:9100/webhook")
TG_TOKEN = os.getenv("TG_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")

# Initialize FastAPI app
app = FastAPI(
    title="EQ12 Compliance Bot",
    description="GitHub App for EQ12 GODSTACK governance automation",
    version="1.0.0",
)


# Models
class WebhookPayload(BaseModel):
    action: str
    repository: dict[str, Any]
    pull_request: dict[str, Any] | None = None
    workflow_run: dict[str, Any] | None = None


class ComplianceCheck(BaseModel):
    pr_number: int
    sensitive: bool
    template_used: bool
    codeowners_approved: bool
    gates_passed: dict[str, bool]


# GitHub App authentication
def get_github_app_token() -> str:
    """Generate GitHub App installation token."""
    if not GITHUB_APP_ID or not Path(GITHUB_PRIVATE_KEY_PATH).exists():
        raise HTTPException(status_code=500, detail="GitHub App not configured")

    with open(GITHUB_PRIVATE_KEY_PATH) as f:
        private_key = f.read()

    # Create JWT
    now = datetime.utcnow()
    payload = {
        "iat": now,
        "exp": now.timestamp() + 600,  # 10 minutes
        "iss": GITHUB_APP_ID,
    }

    token = jwt.encode(payload, private_key, algorithm="RS256")
    return token


def get_installation_token(repo_owner: str, repo_name: str) -> str:
    """Get installation access token for specific repository."""
    app_token = get_github_app_token()

    # Get installation ID
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/installation"
    headers = {
        "Authorization": f"Bearer {app_token}",
        "Accept": "application/vnd.github.v3+json",
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to get installation ID")

    installation_id = response.json()["id"]

    # Get installation token
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    response = requests.post(url, headers=headers)
    if response.status_code != 201:
        raise HTTPException(status_code=500, detail="Failed to get installation token")

    return response.json()["token"]


# GitHub API helpers
def github_api_request(
    method: str, url: str, repo_owner: str, repo_name: str, data: dict | None = None
) -> dict:
    """Make authenticated GitHub API request."""
    token = get_installation_token(repo_owner, repo_name)
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    if method.upper() == "GET":
        response = requests.get(url, headers=headers)
    elif method.upper() == "POST":
        response = requests.post(url, headers=headers, json=data)
    elif method.upper() == "PATCH":
        response = requests.patch(url, headers=headers, json=data)
    else:
        raise ValueError("Unsupported HTTP method")

    if response.status_code not in [200, 201]:
        logger.error(f"GitHub API error: {response.status_code} - {response.text}")
        return {}

    return response.json()


def add_pr_comment(repo_owner: str, repo_name: str, pr_number: int, comment: str):
    """Add comment to pull request."""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues/{pr_number}/comments"
    data = {"body": comment}
    github_api_request("POST", url, repo_owner, repo_name, data)


def add_pr_label(repo_owner: str, repo_name: str, pr_number: int, labels: list):
    """Add labels to pull request."""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues/{pr_number}/labels"
    data = {"labels": labels}
    github_api_request("POST", url, repo_owner, repo_name, data)


def get_pr_info(repo_owner: str, repo_name: str, pr_number: int) -> dict:
    """Get pull request information including files changed."""
    # GraphQL query for comprehensive PR data
    query = """
    query($owner: String!, $name: String!, $number: Int!) {
      repository(owner: $owner, name: $name) {
        pullRequest(number: $number) {
          number
          title
          body
          labels(first: 10) {
            nodes { name }
          }
          files(first: 100) {
            nodes { path }
          }
          commits(last: 1) {
            nodes {
              commit {
                statusCheckRollup {
                  state
                  contexts(first: 100) {
                    nodes {
                      ... on StatusContext {
                        context
                        state
                      }
                      ... on CheckRun {
                        name
                        status
                        conclusion
                      }
                    }
                  }
                }
              }
            }
          }
          reviews(states: APPROVED) {
            totalCount
          }
        }
      }
    }
    """

    variables = {"owner": repo_owner, "name": repo_name, "number": pr_number}

    token = get_installation_token(repo_owner, repo_name)
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    response = requests.post(
        "https://api.github.com/graphql",
        headers=headers,
        json={"query": query, "variables": variables},
    )

    if response.status_code == 200:
        data = response.json()
        return data.get("data", {}).get("repository", {}).get("pullRequest", {})

    return {}


def send_telegram_alert(message: str):
    """Send alert to Telegram."""
    if not TG_TOKEN or not TG_CHAT_ID:
        logger.warning("Telegram not configured")
        return

    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    data = {"chat_id": TG_CHAT_ID, "text": message, "parse_mode": "Markdown"}

    try:
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            logger.info("Telegram alert sent")
        else:
            logger.error(f"Telegram error: {response.text}")
    except Exception as e:
        logger.error(f"Failed to send Telegram alert: {e}")


# Compliance logic
def check_sensitive_pr(files_changed: list) -> bool:
    """Check if PR modifies sensitive business stacks."""
    sensitive_paths = [
        "betting/",
        "odds_parser.py",
        "parlay_builder.py",
        "cannabis/",
        "credit/",
        ".github/CODEOWNERS",
        ".github/workflows/",
        "SECURITY.md",
        "COMPLIANCE.md",
    ]

    for file_path in files_changed:
        for sensitive_path in sensitive_paths:
            if file_path.startswith(sensitive_path):
                return True

    return False


def check_pr_template(pr_body: str, is_sensitive: bool) -> bool:
    """Check if correct PR template was used."""
    if is_sensitive:
        # Check for sensitive template markers
        required_markers = [
            "Business Stack Impact",
            "Compliance Checklist",
            "Regulatory Considerations",
        ]
        return all(marker in pr_body for marker in required_markers)
    # Check for general template markers
    return "## Description" in pr_body and "## Testing" in pr_body


def analyze_pr_compliance(repo_owner: str, repo_name: str, pr_number: int) -> ComplianceCheck:
    """Analyze PR for compliance with governance rules."""
    pr_info = get_pr_info(repo_owner, repo_name, pr_number)

    if not pr_info:
        return ComplianceCheck(
            pr_number=pr_number,
            sensitive=False,
            template_used=False,
            codeowners_approved=False,
            gates_passed={"secrets": False, "security": False, "ci": False},
        )

    # Extract file paths
    files_changed = [file["path"] for file in pr_info.get("files", {}).get("nodes", [])]

    # Check if sensitive
    is_sensitive = check_sensitive_pr(files_changed)

    # Check template usage
    template_used = check_pr_template(pr_info.get("body", ""), is_sensitive)

    # Check CODEOWNERS approval (simplified - check if there are any approvals)
    codeowners_approved = pr_info.get("reviews", {}).get("totalCount", 0) > 0

    # Check governance gates from status checks
    gates_passed = {"secrets": True, "security": True, "ci": True}

    commit_status = pr_info.get("commits", {}).get("nodes", [])
    if commit_status:
        contexts = (
            commit_status[0]
            .get("commit", {})
            .get("statusCheckRollup", {})
            .get("contexts", {})
            .get("nodes", [])
        )
        for context in contexts:
            if (
                "secret" in context.get("context", "").lower()
                or "secret" in context.get("name", "").lower()
            ):
                gates_passed["secrets"] = (
                    context.get("state") == "SUCCESS" or context.get("conclusion") == "success"
                )
            elif (
                "security" in context.get("context", "").lower()
                or "codeql" in context.get("name", "").lower()
            ):
                gates_passed["security"] = (
                    context.get("state") == "SUCCESS" or context.get("conclusion") == "success"
                )
            elif (
                "ci" in context.get("context", "").lower()
                or "test" in context.get("name", "").lower()
            ):
                gates_passed["ci"] = (
                    context.get("state") == "SUCCESS" or context.get("conclusion") == "success"
                )

    return ComplianceCheck(
        pr_number=pr_number,
        sensitive=is_sensitive,
        template_used=template_used,
        codeowners_approved=codeowners_approved,
        gates_passed=gates_passed,
    )


# Webhook verification
def verify_webhook_signature(payload_body: bytes, signature_header: str) -> bool:
    """Verify GitHub webhook signature."""
    if not GITHUB_WEBHOOK_SECRET:
        logger.warning("GitHub webhook secret not configured")
        return True  # Allow in development

    if not signature_header:
        return False

    hash_object = hmac.new(
        GITHUB_WEBHOOK_SECRET.encode("utf-8"),
        msg=payload_body,
        digestmod=hashlib.sha256,
    )
    expected_signature = "sha256=" + hash_object.hexdigest()

    return hmac.compare_digest(expected_signature, signature_header)


# Webhook handlers
async def handle_pull_request_opened(payload: dict):
    """Handle pull request opened event."""
    repo = payload["repository"]
    pr = payload["pull_request"]

    repo_owner = repo["owner"]["login"]
    repo_name = repo["name"]
    pr_number = pr["number"]
    pr_title = pr["title"]

    logger.info(f"PR opened: #{pr_number} - {pr_title}")

    # Analyze compliance
    compliance = analyze_pr_compliance(repo_owner, repo_name, pr_number)

    # Handle sensitive PRs
    if compliance.sensitive:
        labels_to_add = ["governance-review"]

        # Determine specific sensitive label
        pr_info = get_pr_info(repo_owner, repo_name, pr_number)
        files_changed = [file["path"] for file in pr_info.get("files", {}).get("nodes", [])]

        if any(
            f.startswith("betting/") or f in ["odds_parser.py", "parlay_builder.py"]
            for f in files_changed
        ):
            labels_to_add.append("⚠ Sensitive: Betting")
        if any(f.startswith("cannabis/") for f in files_changed):
            labels_to_add.append("⚠ Sensitive: Cannabis")
        if any(f.startswith("credit/") for f in files_changed):
            labels_to_add.append("⚠ Sensitive: Credit")

        add_pr_label(repo_owner, repo_name, pr_number, labels_to_add)

        # Check template usage
        if not compliance.template_used:
            comment = """
🚨 **Sensitive Business Stack Detected**

This PR modifies sensitive business logic. Please ensure you're using the correct PR template:
- Use `.github/PULL_REQUEST_TEMPLATE/sensitive_module.md`
- Complete the compliance checklist
- Verify regulatory considerations

Required approvals: CODEOWNERS (@Vibehigheric)
            """
            add_pr_comment(repo_owner, repo_name, pr_number, comment.strip())

            # Send Telegram alert
            alert_msg = f"🚨 **EQ12 Compliance Alert**\n\nPR #{pr_number}: {pr_title}\n- Sensitive stack modified\n- Missing proper template\n- Requires immediate attention"
            send_telegram_alert(alert_msg)

    # Add standard governance label
    add_pr_label(repo_owner, repo_name, pr_number, ["needs-review"])


async def handle_workflow_run_completed(payload: dict):
    """Handle workflow run completed event."""
    repo = payload["repository"]
    workflow_run = payload["workflow_run"]

    repo_owner = repo["owner"]["login"]
    repo_name = repo["name"]
    workflow_name = workflow_run["name"]
    conclusion = workflow_run["conclusion"]

    # Find associated PRs
    prs = workflow_run.get("pull_requests", [])

    for pr in prs:
        pr_number = pr["number"]

        if conclusion == "failure":
            # Determine which gate failed
            gate_type = "ci"
            if "secret" in workflow_name.lower():
                gate_type = "secrets"
            elif "security" in workflow_name.lower() or "codeql" in workflow_name.lower():
                gate_type = "security"

            # Add failure comment
            comment = f"❌ **Governance Gate Failed: {gate_type.title()}**\n\nWorkflow `{workflow_name}` failed. Please review and fix the issues before merge."
            add_pr_comment(repo_owner, repo_name, pr_number, comment)

            # Add failure label
            add_pr_label(repo_owner, repo_name, pr_number, [f"{gate_type}-fail"])

            # Send Telegram alert for sensitive PRs
            compliance = analyze_pr_compliance(repo_owner, repo_name, pr_number)
            if compliance.sensitive:
                alert_msg = f"🚨 **EQ12 Governance Failure**\n\nPR #{pr_number} (Sensitive)\nFailed gate: {gate_type.title()}\nWorkflow: {workflow_name}"
                send_telegram_alert(alert_msg)

        elif conclusion == "success":
            # Remove failure labels if they exist
            logger.info(f"Workflow {workflow_name} succeeded for PR #{pr_number}")


# FastAPI routes
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "EQ12 Compliance Bot",
        "version": "1.0.0",
        "status": "operational",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "github_app_configured": bool(GITHUB_APP_ID and Path(GITHUB_PRIVATE_KEY_PATH).exists()),
        "telegram_configured": bool(TG_TOKEN and TG_CHAT_ID),
    }


@app.post("/webhook")
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    """Handle GitHub webhook events."""
    # Verify signature
    signature = request.headers.get("X-Hub-Signature-256")
    payload_body = await request.body()

    if not verify_webhook_signature(payload_body, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")

    # Parse payload
    payload = json.loads(payload_body)
    event_type = request.headers.get("X-GitHub-Event")

    logger.info(f"Received GitHub webhook: {event_type}")

    # Route to appropriate handler
    if event_type == "pull_request" and payload.get("action") == "opened":
        background_tasks.add_task(handle_pull_request_opened, payload)
    elif event_type == "workflow_run" and payload.get("action") == "completed":
        background_tasks.add_task(handle_workflow_run_completed, payload)

    return JSONResponse({"status": "received"})


@app.get("/pr/{pr_number}/compliance")
async def get_pr_compliance(
    pr_number: int, repo_owner: str = "Vibehigheric", repo_name: str = "edgegod-parlay"
):
    """Get compliance status for a specific PR."""
    compliance = analyze_pr_compliance(repo_owner, repo_name, pr_number)
    return compliance


@app.post("/copilot/check-pr")
async def copilot_check_pr(
    pr_number: int, repo_owner: str = "Vibehigheric", repo_name: str = "edgegod-parlay"
):
    """Copilot extension endpoint for PR compliance check."""
    compliance = analyze_pr_compliance(repo_owner, repo_name, pr_number)

    # Format response for Copilot
    response = f"**PR #{pr_number} Governance Status:**\n\n"

    if compliance.sensitive:
        response += "⚠️ **Sensitive Business Stack Detected**\n"

    response += f"✅ Template Used: {'Yes' if compliance.template_used else '❌ No'}\n"
    response += f"✅ CODEOWNERS Approved: {'Yes' if compliance.codeowners_approved else '❌ No'}\n"

    response += "\n**Governance Gates:**\n"
    for gate, passed in compliance.gates_passed.items():
        status = "✅ Passed" if passed else "❌ Failed"
        response += f"- {gate.title()}: {status}\n"

    overall_status = (
        "✅ Ready for merge"
        if all(
            [
                compliance.template_used,
                compliance.codeowners_approved if compliance.sensitive else True,
                all(compliance.gates_passed.values()),
            ]
        )
        else "❌ Blocked"
    )

    response += f"\n**Overall Status:** {overall_status}"

    return {"response": response}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8001"))
    uvicorn.run("compliance_bot:app", host="0.0.0.0", port=port, reload=True)
