"""
Tool: github_tool
Description: Interact with GitHub repositories via the GitHub REST API.
             Agents use this to read PRs, issues, file contents from repos,
             and post comments — without leaving the chat.

Usage in OpenWebUI:
  - Workspace → Tools → New Tool → paste this file.
  - Set GITHUB_TOKEN in your environment or OpenWebUI secrets.
  - Enable in Dev Agent and Architect Agent configurations.

Required env var: GITHUB_TOKEN (classic token with repo scope)
"""

import os
import json
from typing import Optional
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


GITHUB_API = "https://api.github.com"
TOKEN = os.environ.get("GITHUB_TOKEN", "")


def _request(method: str, endpoint: str, body: Optional[dict] = None) -> dict:
    url = f"{GITHUB_API}{endpoint}"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
    }
    data = json.dumps(body).encode() if body else None
    req = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.reason}", "url": url}
    except URLError as e:
        return {"error": f"URL error: {e.reason}"}


def get_pull_request(owner: str, repo: str, pr_number: int) -> str:
    """
    Get details of a Pull Request.

    Args:
        owner: Repository owner (user or org).
        repo: Repository name.
        pr_number: PR number.

    Returns:
        Formatted PR summary as string.
    """
    pr = _request("GET", f"/repos/{owner}/{repo}/pulls/{pr_number}")
    if "error" in pr:
        return f"[ERROR] {pr['error']}"

    files = _request("GET", f"/repos/{owner}/{repo}/pulls/{pr_number}/files")
    file_list = ""
    if isinstance(files, list):
        file_list = "\n".join(
            f"  - {f['filename']} (+{f['additions']}/-{f['deletions']})" for f in files[:20]
        )

    return f"""## PR #{pr_number}: {pr.get('title')}

**State:** {pr.get('state')} | **Draft:** {pr.get('draft')}  
**Author:** {pr.get('user', {}).get('login')}  
**Branch:** `{pr.get('head', {}).get('ref')}` → `{pr.get('base', {}).get('ref')}`  
**URL:** {pr.get('html_url')}

### Description
{pr.get('body') or '_No description_'}

### Changed Files ({len(files) if isinstance(files, list) else '?'})
{file_list}
"""


def list_issues(owner: str, repo: str, state: str = "open", limit: int = 20) -> str:
    """
    List issues in a repository.

    Args:
        owner: Repository owner.
        repo: Repository name.
        state: 'open', 'closed', or 'all'.
        limit: Max number of issues to return.

    Returns:
        Formatted list of issues.
    """
    issues = _request("GET", f"/repos/{owner}/{repo}/issues?state={state}&per_page={limit}")
    if isinstance(issues, dict) and "error" in issues:
        return f"[ERROR] {issues['error']}"

    if not issues:
        return "No issues found."

    lines = [f"## Issues ({state}) — {owner}/{repo}\n"]
    for issue in issues:
        if "pull_request" in issue:
            continue  # skip PRs listed as issues
        labels = ", ".join(l["name"] for l in issue.get("labels", []))
        lines.append(
            f"- **#{issue['number']}** {issue['title']} "
            f"[{labels or 'no labels'}] — @{issue['user']['login']}"
        )

    return "\n".join(lines)


def get_file_content(owner: str, repo: str, file_path: str, ref: str = "main") -> str:
    """
    Get the content of a file in a GitHub repository.

    Args:
        owner: Repository owner.
        repo: Repository name.
        file_path: Path to the file in the repo.
        ref: Branch, tag, or commit SHA.

    Returns:
        File content as string.
    """
    import base64
    data = _request("GET", f"/repos/{owner}/{repo}/contents/{file_path}?ref={ref}")
    if "error" in data:
        return f"[ERROR] {data['error']}"
    if data.get("encoding") == "base64":
        content = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
        return f"# {file_path} @ {ref}\n\n{content}"
    return f"[ERROR] Unexpected encoding: {data.get('encoding')}"


def create_issue_comment(owner: str, repo: str, issue_number: int, body: str) -> str:
    """
    Post a comment on an issue or PR.

    Args:
        owner: Repository owner.
        repo: Repository name.
        issue_number: Issue or PR number.
        body: Comment body in markdown.

    Returns:
        Success message or error.
    """
    result = _request("POST", f"/repos/{owner}/{repo}/issues/{issue_number}/comments", {"body": body})
    if "error" in result:
        return f"[ERROR] {result['error']}"
    return f"✅ Comment posted: {result.get('html_url')}"
