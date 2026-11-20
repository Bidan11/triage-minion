"""GitHub fetch parsing (fixture, no network) and actions planning (fix 2)."""

import json
from pathlib import Path

from github_actions import check_ownership, comment_body, plan_actions
from github_client import parse_github_issues
from triage import classify_issue

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "github_issues.json"


def test_parse_filters_pull_requests_and_maps_fields():
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert any("pull_request" in item for item in payload)  # fixture sanity
    issues = parse_github_issues(payload)
    numbers = [i["id"] for i in issues]
    assert 822 not in numbers  # the PR item is filtered out
    assert numbers == [821, 813]
    first = issues[0]
    assert first["html_url"] == "https://github.com/openminion/openminion/issues/821"
    assert first["title"].startswith("fetch URL policy crashes")
    assert first["created_at"] == "2026-11-20T17:00:56Z"
    labelled = next(i for i in issues if i["id"] == 813)
    assert "enhancement" in labelled["labels"]


def test_plan_actions_shape():
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    issues = parse_github_issues(payload)
    decisions = [classify_issue(i) for i in issues]
    actions = plan_actions(decisions)
    assert [a["issue"] for a in actions] == [821, 813]
    for action, decision in zip(actions, decisions):
        assert action["labels"] == decision["suggested_labels"]
        assert "TriageMinion triage summary" in action["comment"]
        assert decision["category"] in action["comment"]


def test_comment_body_mentions_missing_info():
    decision = classify_issue(
        {"id": 1, "title": "Crash on start", "body": "It crashes."}
    )
    body = comment_body(decision)
    assert "version / environment" in body


def test_ownership_check():
    assert check_ownership("Bidan11", "bidan11") is True
    assert check_ownership("OpenMinion", "Bidan11") is False
