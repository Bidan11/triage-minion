"""
The single TriageMinion report renderer, plus validation and repair.

Fix 10: ONE renderer serves every path — the offline fallback mode,
the online model mode, and the repair step — so a triage report always
has the same shape regardless of who produced the decisions.

Fix 4: every issue appears with its FULL, untruncated title and, when a
URL is known, a clickable Markdown link to the issue.

Fix 5: after any run, the recorded decisions are validated against the
input issues. Issues the model never recorded (a partial run) are
filled in by the fallback classifier and clearly labelled, so a
half-finished run can no longer silently become the final report.
"""

from __future__ import annotations

import re

from triage import classify_issue


def _cell(text: object) -> str:
    """Escape a value for a Markdown table cell (titles stay whole —
    only the characters that would break the table are neutralised)."""
    return str(text).replace("|", "/").replace("\n", " ").strip()


def _issue_ref(decision: dict) -> str:
    """'[#774](url)' when a URL is known, else '#774'."""
    iid = decision.get("id")
    url = decision.get("url")
    if url:
        return f"[#{iid}]({url})"
    return f"#{iid}"


def _title_ref(decision: dict) -> str:
    title = _cell(decision.get("title", "(untitled)"))
    url = decision.get("url")
    if url:
        return f"[{title}]({url})"
    return title


def render_report(decisions: list[dict], source: str) -> str:
    """Render the canonical triage report from decision dicts.

    Decision shape (produced by the model via ``record_triage`` or by
    the fallback classifier): id, title, url, category, priority,
    missing_info (list), suggested_labels (list), reason, decided_by.
    """
    by_model = sum(1 for d in decisions if d.get("decided_by") == "model")
    by_fallback = len(decisions) - by_model
    if by_fallback and by_model:
        decided_line = (
            f"Decisions: {by_model} by the model, {by_fallback} by the "
            "fallback keyword rules (model run incomplete — repaired, see below)."
        )
    elif by_fallback:
        decided_line = "Decisions: fallback keyword rules (no model run)."
    else:
        decided_line = "Decisions: recorded by the model via the record_triage tool."

    counts: dict[str, int] = {}
    for d in decisions:
        counts[d["category"]] = counts.get(d["category"], 0) + 1
    summary = ", ".join(
        f"{n} {cat}" for cat, n in sorted(counts.items(), key=lambda kv: -kv[1])
    )

    lines = [
        "# Triage Report",
        "",
        f"Source: `{source}` - {len(decisions)} issue(s) triaged.",
        decided_line,
        "",
        f"**Snapshot:** {summary}.",
        "",
        "| # | Issue | Category | Priority | Missing info | Suggested labels |",
        "|---|-------|----------|----------|--------------|------------------|",
    ]
    for d in decisions:
        missing = ", ".join(d.get("missing_info") or []) or "-"
        labels = ", ".join(f"`{l}`" for l in d.get("suggested_labels") or []) or "-"
        lines.append(
            f"| {_issue_ref(d)} | {_title_ref(d)} | {d['category']} | "
            f"{d['priority']} | {_cell(missing)} | {labels} |"
        )

    top = [d for d in decisions if d["priority"] in ("P0", "P1")]
    if top:
        lines += ["", "## Top priority", ""]
        for d in top:
            reason = _cell(d.get("reason", ""))
            lines.append(
                f"- {_issue_ref(d)} {_title_ref(d)} — {d['priority']} / "
                f"{d['category']}" + (f": {reason}" if reason else "")
            )

    lacking = [d for d in decisions if d.get("missing_info")]
    if lacking:
        lines += ["", "## Information to request from reporters", ""]
        for d in lacking:
            lines.append(
                f"- {_issue_ref(d)} {_title_ref(d)} — missing: "
                + ", ".join(d["missing_info"])
            )

    repaired = [d for d in decisions if d.get("repaired")]
    if repaired:
        ids = ", ".join(f"#{d['id']}" for d in repaired)
        lines += [
            "",
            "## Repaired entries",
            "",
            f"The model run did not record decisions for: {ids}. Those "
            "entries above come from the fallback keyword rules and are "
            "marked as such; re-run with a model to replace them.",
        ]

    lines += [
        "",
        "Next step: a maintainer reviews this draft before any label is applied.",
        "",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Validation and repair (fix 5)
# ---------------------------------------------------------------------------

def validate_decisions(issues: list[dict], decisions: list[dict]) -> dict:
    """Compare recorded decisions against the input issues.

    Returns {"missing": [...], "duplicates": [...], "extra": [...]} —
    issue ids with no decision, ids decided more than once, and
    decisions that match no input issue.
    """
    wanted = [i.get("id") for i in issues]
    seen: dict = {}
    for d in decisions:
        seen[d.get("id")] = seen.get(d.get("id"), 0) + 1
    return {
        "missing": [i for i in wanted if seen.get(i, 0) == 0],
        "duplicates": [i for i, n in seen.items() if n > 1 and i in wanted],
        "extra": [i for i in seen if i not in wanted],
    }


def ensure_complete_decisions(
    issues: list[dict],
    decisions: list[dict],
    repo: str | None = None,
) -> tuple[list[dict], list]:
    """Return (complete decisions in input order, repaired issue ids).

    Duplicates collapse to the first decision; decisions for unknown
    issues are dropped; every issue left without a decision is filled
    by the fallback classifier and flagged ``repaired=True`` so the
    report can disclose it.
    """
    by_id: dict = {}
    for d in decisions:
        by_id.setdefault(d.get("id"), d)
    complete: list[dict] = []
    repaired: list = []
    for issue in issues:
        iid = issue.get("id")
        if iid in by_id:
            complete.append(by_id[iid])
        else:
            fill = classify_issue(issue, repo=repo)
            fill["repaired"] = True
            complete.append(fill)
            repaired.append(iid)
    return complete, repaired


def covered_issue_ids(report_text: str, issues: list[dict]) -> set:
    """Issue ids a rendered report actually covers (one table row each).

    Used to double-check a report file on disk: a row counts when a
    line starts with the issue's ref (``| #774`` or ``| [#774](...)``).
    """
    covered = set()
    for issue in issues:
        iid = issue.get("id")
        pattern = re.compile(rf"^\|\s*\[?#?{re.escape(str(iid))}\b", re.MULTILINE)
        if pattern.search(report_text):
            covered.add(iid)
    return covered
