"""Fallback classifier expectations (fixes 6 and 7).

The 16 known issues (6 samples + 10 real OpenMinion issues) are the
regression set: their category / priority / missing-info results were
verified by hand against the old reports and must not drift.
"""

import json
from pathlib import Path

import pytest

from triage import classify_issue, reporter_provided_environment

ROOT = Path(__file__).resolve().parent.parent
SAMPLES = json.loads((ROOT / "sample_issues.json").read_text(encoding="utf-8"))
REAL = json.loads((ROOT / "real_issues.json").read_text(encoding="utf-8"))
BY_ID = {i["id"]: i for i in SAMPLES + REAL}

EXPECTED = {
    # sample issues: id -> (category, priority, missing_info)
    101: ("bug", "P0", ["reproduction steps"]),
    102: ("feature", "P3", []),
    103: ("docs", "P3", []),
    104: ("security", "P0", ["version / environment", "reproduction steps"]),
    105: ("bug", "P1", ["version / environment", "reproduction steps"]),
    106: ("question", "P3", []),
    # real OpenMinion issues
    774: ("bug", "P2", []),
    773: ("bug", "P3", []),
    770: ("bug", "P2", []),
    769: ("bug", "P2", []),
    767: ("feature", "P3", []),
    766: ("bug", "P2", []),
    759: ("feature", "P2", []),
    757: ("bug", "P3", ["version / environment", "reproduction steps"]),
    754: ("bug", "P2", ["version / environment", "reproduction steps"]),
    752: ("bug", "P1", ["version / environment", "reproduction steps"]),
}


@pytest.mark.parametrize("issue_id", sorted(EXPECTED))
def test_known_issues(issue_id):
    decision = classify_issue(BY_ID[issue_id])
    category, priority, missing = EXPECTED[issue_id]
    assert decision["category"] == category
    assert decision["priority"] == priority
    assert decision["missing_info"] == missing
    assert decision["decided_by"] == "fallback"


def test_real_issues_are_8_bug_2_feature():
    cats = [classify_issue(i)["category"] for i in REAL]
    assert cats.count("bug") == 8
    assert cats.count("feature") == 2
    features = {i["id"] for i in REAL if classify_issue(i)["category"] == "feature"}
    assert features == {767, 759}


# --- fix 6: the hardened fragilities -------------------------------------

def test_bare_add_does_not_force_feature():
    issue = {"id": 1, "title": "Crash when clicking the Add button",
             "body": "The app crashes with an error as soon as I click Add. Steps to reproduce: open the form, click Add."}
    assert classify_issue(issue)["category"] == "bug"


def test_bare_question_mark_does_not_force_question():
    issue = {"id": 2, "title": "Export broken?",
             "body": "Clicking export does nothing at all. It is stuck forever."}
    assert classify_issue(issue)["category"] == "bug"


def test_bare_500_does_not_force_p1():
    issue = {"id": 3, "title": "Support 500 users in one workspace",
             "body": "Feature request: our team has 500 users and we would like them all in one workspace."}
    decision = classify_issue(issue)
    assert decision["category"] == "feature"
    assert decision["priority"] == "P3"


def test_http_500_in_error_context_is_p1():
    issue = {"id": 4, "title": "Export sometimes fails",
             "body": "Exporting sometimes fails with a 500 error and is slow."}
    assert classify_issue(issue)["priority"] == "P1"


def test_security_word_alone_does_not_force_security():
    issue = {"id": 5, "title": "Add a security settings page",
             "body": "Feature request: users want one page where they can manage their security preferences and notifications."}
    assert classify_issue(issue)["category"] == "feature"


def test_strong_security_evidence_forces_security():
    issue = {"id": 6, "title": "XSS in comment rendering (CVE-2026-1234)",
             "body": "A stored cross-site scripting vulnerability: an attacker can inject a script that runs for every viewer."}
    decision = classify_issue(issue)
    assert decision["category"] == "security"
    assert decision["priority"] == "P0"


# --- fix 7: environment judged from the body only -------------------------

def test_title_version_tag_alone_is_not_environment():
    issue = {"id": 7, "title": "[1.2.3] Widget crashes on save",
             "body": "Pressing save crashes the widget every time."}
    assert reporter_provided_environment(issue) is False
    assert "version / environment" in classify_issue(issue)["missing_info"]


def test_body_environment_section_counts():
    issue = {"id": 8, "title": "Widget crashes on save",
             "body": "Environment: Python 3.12 on Windows 11. Pressing save crashes the widget."}
    assert reporter_provided_environment(issue) is True
    assert "version / environment" not in classify_issue(issue)["missing_info"]
