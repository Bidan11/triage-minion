"""Unified renderer, validation and partial-report repair (fixes 4, 5, 10)."""

import json
import re
from pathlib import Path

from report import (
    covered_issue_ids,
    ensure_complete_decisions,
    render_report,
    validate_decisions,
)
from triage import classify_issue

ROOT = Path(__file__).resolve().parent.parent
REAL = json.loads((ROOT / "real_issues.json").read_text(encoding="utf-8"))
REPO = "OpenMinion/openminion"


def _rows(text):
    return [
        l for l in text.splitlines()
        if re.match(r"\| \[?#\d", l)  # data rows only, not the "| # |" header
    ]


def test_renderer_links_and_full_titles():
    decisions = [classify_issue(i, repo=REPO) for i in REAL]
    text = render_report(decisions, "real_issues.json")
    for issue in REAL:
        url = f"https://github.com/{REPO}/issues/{issue['id']}"
        assert f"[{issue['title']}]({url})" in text  # full title, clickable
        assert "..." not in text.split(url)[0].splitlines()[-1]  # never truncated
    assert len(_rows(text)) == len(REAL)


def test_renderer_covers_every_issue_exactly_once():
    decisions = [classify_issue(i, repo=REPO) for i in REAL]
    text = render_report(decisions, "real_issues.json")
    assert covered_issue_ids(text, REAL) == {i["id"] for i in REAL}
    for issue in REAL:
        rows = [l for l in _rows(text) if re.search(rf"#?{issue['id']}\b", l.split("|")[1])]
        assert len(rows) == 1


def test_renderer_without_urls_degrades_gracefully():
    samples = json.loads((ROOT / "sample_issues.json").read_text(encoding="utf-8"))
    decisions = [classify_issue(i) for i in samples]
    text = render_report(decisions, "sample_issues.json")
    assert "App crash on login after 2.4.0 update" in text
    assert "github.com" not in text


def test_validate_decisions_reports_gaps():
    partial = [classify_issue(i) for i in REAL[:6]]
    check = validate_decisions(REAL, partial)
    assert check["missing"] == [i["id"] for i in REAL[6:]]
    dup = partial + [partial[0]]
    assert validate_decisions(REAL, dup)["duplicates"] == [REAL[0]["id"]]


def test_partial_run_is_repaired_and_disclosed():
    """Fix 5: a model run that recorded only 6 of 10 issues must not
    become the final report as-is — gaps are fallback-filled, marked,
    and the rendered report covers all 10 exactly once."""
    partial = []
    for issue in REAL[:6]:
        d = classify_issue(issue, repo=REPO)
        d["decided_by"] = "model"
        partial.append(d)
    complete, repaired = ensure_complete_decisions(REAL, partial, repo=REPO)
    assert repaired == [i["id"] for i in REAL[6:]]
    assert len(complete) == len(REAL)
    assert all(d["decided_by"] == "model" for d in complete[:6])
    assert all(d.get("repaired") for d in complete[6:])
    text = render_report(complete, "real_issues.json")
    assert covered_issue_ids(text, REAL) == {i["id"] for i in REAL}
    assert "Repaired entries" in text
    for iid in repaired:
        assert f"#{iid}" in text.split("Repaired entries")[1]


def test_duplicate_decisions_collapse_to_first():
    d = classify_issue(REAL[0], repo=REPO)
    complete, repaired = ensure_complete_decisions(REAL, [d, dict(d)], repo=REPO)
    assert len(complete) == len(REAL)
    assert complete[0] is d
    assert repaired == [i["id"] for i in REAL[1:]]
