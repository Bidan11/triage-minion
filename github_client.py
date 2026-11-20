"""
Minimal GitHub REST client for TriageMinion (fix 2).

Read path: fetch open issues from any public repository — no token
required; an optional ``GITHUB_TOKEN`` env var raises the rate limit.
This is what turns TriageMinion from "reads a JSON file someone
exported" into an agent connected to a real repository.

Only the standard library is used (``urllib``), so the offline mode
and the test suite need no extra dependencies.
"""

from __future__ import annotations

import json
import os
import urllib.request

API_ROOT = "https://api.github.com"
USER_AGENT = "TriageMinion/0.2 (Cortensor Hackathon #5)"


def _request(path: str, token: str | None = None, method: str = "GET",
             payload: dict | None = None) -> tuple[int, object]:
    """One GitHub API call. Returns (status, parsed JSON or None)."""
    url = path if path.startswith("http") else f"{API_ROOT}{path}"
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", USER_AGENT)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, (json.loads(body) if body else None)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        try:
            parsed = json.loads(body) if body else None
        except json.JSONDecodeError:
            parsed = None
        return exc.code, parsed


def parse_github_issues(payload: list) -> list[dict]:
    """Map a GitHub ``GET /repos/{o}/{r}/issues`` payload to TriageMinion
    issue dicts. Pull requests (which the issues endpoint interleaves)
    are filtered out."""
    issues = []
    for item in payload:
        if not isinstance(item, dict) or "pull_request" in item:
            continue
        issues.append(
            {
                "id": item.get("number"),
                "title": item.get("title", "(untitled)"),
                "body": item.get("body") or "",
                "html_url": item.get("html_url"),
                "labels": [
                    l.get("name") for l in item.get("labels", [])
                    if isinstance(l, dict)
                ],
                "created_at": item.get("created_at"),
            }
        )
    return issues


def fetch_open_issues(
    repo: str,
    limit: int = 10,
    token: str | None = None,
) -> list[dict]:
    """Fetch up to ``limit`` open issues from ``owner/repo``, newest
    first. Raises RuntimeError on an API error."""
    token = token if token is not None else os.environ.get("GITHUB_TOKEN")
    # The issues endpoint interleaves pull requests, so page through
    # results until `limit` real issues are collected (or the repo runs
    # out of open items).
    issues: list[dict] = []
    page = 1
    while len(issues) < limit:
        status, payload = _request(
            f"/repos/{repo}/issues?state=open&per_page=100&page={page}"
            "&sort=created&direction=desc",
            token=token,
        )
        if status != 200 or not isinstance(payload, list):
            raise RuntimeError(
                f"GitHub API error {status} fetching {repo}: {payload}"
            )
        if not payload:
            break
        issues.extend(parse_github_issues(payload))
        page += 1
    return issues[:limit]


def fetch_authenticated_login(token: str) -> str:
    """The login name owning ``token`` (GET /user). Used by the actions
    module to prove a repo belongs to the token's owner before writing."""
    status, payload = _request("/user", token=token)
    if status != 200 or not isinstance(payload, dict) or "login" not in payload:
        raise RuntimeError(f"GitHub API error {status} on GET /user: {payload}")
    return str(payload["login"])
