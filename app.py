"""
TriageMinion - a GitHub issue triage agent built on the OpenMinion 0.1 Python SDK.

Workflow (one useful, repeatable job):
  1. Load issues — from a JSON file, or fetched live from a GitHub
     repository with ``--github owner/repo``.
  2. The MODEL classifies each issue itself (category, priority,
     suggested labels, missing information, a one-line reason) after
     reading the title and body through a paged tool, and records every
     decision through the ``record_triage`` tool.
  3. The report is rendered from the recorded decisions by the single
     renderer in ``report.py``. If a run ends with decisions missing
     (a partial run), the gaps are filled by the fallback keyword
     classifier and disclosed in the report (see ``triage.py``).
  4. Applying labels/comments to a real repository is a separate,
     explicit step (``github_actions.py``, dry-run by default, owner's
     own repos only) so a human stays in control.

Run modes:
  * Online (hackathon demo): a real model through OpenMinion classifies.
        python app.py --input sample_issues.json --output report.md
        python app.py --github OpenMinion/openminion --limit 10 --output report.md
    Requires the OpenMinion SDK and a configured model-provider key
    (see README, "Setup").
  * Offline (logic test): the fallback keyword classifier produces the
    decisions; the same renderer writes the report. No model needed.
        python app.py --offline --input sample_issues.json --output report.md
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from github_client import fetch_open_issues
from report import ensure_complete_decisions, render_report, validate_decisions
from triage import CATEGORIES, PRIORITIES, classify_issue, issue_url

PAGE_SIZE = 4  # issues per tool page — see BUILDING_BLOCKS (truncation finding)
BODY_CAP = 1200  # chars of body per issue in the tool payload


def load_issues(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Issue file must be a JSON list of issues.")
    return data


# ---------------------------------------------------------------------------
# Online mode: OpenMinion agent. The model classifies; decisions are
# recorded through record_triage; the report renders from the records.
# ---------------------------------------------------------------------------

def run_online(issues: list[dict], source: str, output_path: Path,
               repo: str | None) -> int:
    try:
        from openminion import Agent, ProviderError, TurnTimeoutError, tool
    except ImportError:
        print(
            "OpenMinion SDK is not installed. Run: pip install -r requirements.txt\n"
            "Or test the workflow without a model: python app.py --offline",
            file=sys.stderr,
        )
        return 2

    recorded: list[dict] = []
    by_id = {i.get("id"): i for i in issues}

    def _page(offset: int) -> list[dict]:
        page = []
        for issue in issues[offset : offset + PAGE_SIZE]:
            body = issue.get("body") or ""
            if len(body) > BODY_CAP:
                body = body[:BODY_CAP] + "\n[body truncated for the tool payload]"
            page.append(
                {
                    "id": issue.get("id"),
                    "title": issue.get("title", "(untitled)"),
                    "body": body,
                    "labels": issue.get("labels", []),
                    "created_at": issue.get("created_at"),
                }
            )
        return page

    @tool
    def get_issue_page(offset: int = 0) -> str:
        """Return one page of raw issues (4 per page) for you to triage.

        Call with offset 0 first, then 4, 8, ... until the page covers
        every issue (see the "total" field). Each issue has its full
        title and body — read them and decide the triage yourself.
        """
        return json.dumps(
            {"total": len(issues), "offset": offset, "issues": _page(offset)}
        )

    @tool
    def record_triage(issue_id: int, category: str, priority: str,
                      labels: str, missing_info: str, reason: str) -> str:
        """Record YOUR triage decision for one issue.

        category: one of bug, feature, docs, security, question.
        priority: one of P0, P1, P2, P3.
        labels: comma-separated suggested labels (e.g. "type:bug, priority:P1").
        missing_info: semicolon-separated items the reporter still owes
        (e.g. "version / environment; reproduction steps"), or "none".
        reason: one short line explaining the decision.
        """
        issue = by_id.get(issue_id)
        if issue is None:
            return f"Unknown issue id {issue_id}; no decision recorded."
        category = category.strip().lower()
        priority = priority.strip().upper()
        if category not in CATEGORIES:
            return f"Invalid category {category!r}; use one of {', '.join(CATEGORIES)}."
        if priority not in PRIORITIES:
            return f"Invalid priority {priority!r}; use one of {', '.join(PRIORITIES)}."
        label_list = [l.strip() for l in labels.split(",") if l.strip()]
        if not label_list:
            label_list = [f"type:{category}", f"priority:{priority}"]
        missing = [
            m.strip() for m in missing_info.split(";")
            if m.strip() and m.strip().lower() != "none"
        ]
        decision = {
            "id": issue_id,
            "title": issue.get("title", "(untitled)"),
            "url": issue_url(issue, repo),
            "category": category,
            "priority": priority,
            "missing_info": missing,
            "suggested_labels": label_list,
            "reason": reason.strip(),
            "decided_by": "model",
        }
        recorded[:] = [d for d in recorded if d["id"] != issue_id] + [decision]
        return f"Recorded triage for #{issue_id} ({len(recorded)}/{len(issues)} recorded)."

    @tool
    def save_report() -> str:
        """Render and save the final report from your recorded decisions.

        Only succeeds once every issue has a recorded decision; if any
        are missing it tells you which ones and saves nothing.
        """
        check = validate_decisions(issues, recorded)
        if check["missing"]:
            return (
                "Cannot save yet — no triage recorded for issue(s): "
                + ", ".join(f"#{i}" for i in check["missing"])
                + ". Record those decisions, then call save_report again."
            )
        complete, _ = ensure_complete_decisions(issues, recorded, repo=repo)
        output_path.write_text(render_report(complete, source), encoding="utf-8")
        return f"Saved report covering all {len(complete)} issues to {output_path}"

    instructions = (
        "You are TriageMinion, an issue triage agent for open-source maintainers. "
        "Your job is to classify every loaded issue YOURSELF. "
        "Call get_issue_page first (offset 0), then keep calling it with the "
        "next offset (4, 8, ...) until you have read every issue (the result "
        "shows the total). "
        "For each issue, judge from its title and body: a category (bug, "
        "feature, docs, security, question), a priority (P0 most urgent to "
        "P3), suggested labels, and — for bugs and security reports — what "
        "information is missing from the reporter (version/environment is "
        "provided only if the BODY states it, not the title; reproduction "
        "steps only if the body gives them). "
        "Record each decision by calling record_triage before moving on. "
        "When every issue is recorded, call save_report to write the final "
        "report. Never invent issues, versions, or error messages that are "
        "not in the issue text, and never end your turn before save_report "
        "succeeds."
    )

    try:
        with Agent(
            instructions=instructions,
            tools=[get_issue_page, record_triage, save_report],
            forced_tools=["get_issue_page"],
            session_id="triage-minion-demo",
        ) as agent:
            result = agent.run(
                f"Triage the {len(issues)} loaded issues and save the report.",
                timeout_seconds=300,
            )
        text = getattr(result, "text", None)
        print(text if text else "Agent run finished.")
    except ProviderError as exc:
        print(f"Model provider error: {exc}", file=sys.stderr)
        return 3
    except TurnTimeoutError as exc:
        print(f"Agent turn timed out: {exc}", file=sys.stderr)
        return 4

    # Fix 5: whatever state the run ended in, the final report must
    # cover every issue exactly once. Gaps are filled by the fallback
    # classifier and disclosed in the report's "Repaired entries".
    complete, repaired = ensure_complete_decisions(issues, recorded, repo=repo)
    output_path.write_text(render_report(complete, source), encoding="utf-8")
    if repaired:
        print(
            "Note: model run left "
            f"{len(repaired)} issue(s) unrecorded ({', '.join(f'#{i}' for i in repaired)}); "
            "the final report fills them with labelled fallback decisions."
        )
    else:
        print(f"Report validated: all {len(complete)} issue(s) covered exactly once.")
    return 0


def run_offline(issues: list[dict], source: str, output_path: Path,
                repo: str | None) -> int:
    decisions = [classify_issue(i, repo=repo) for i in issues]
    complete, _ = ensure_complete_decisions(issues, decisions, repo=repo)
    output_path.write_text(render_report(complete, source), encoding="utf-8")
    print(f"Triaged {len(complete)} issue(s) -> {output_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="TriageMinion - OpenMinion issue triage agent")
    parser.add_argument("--input", default="sample_issues.json", help="JSON file with issues")
    parser.add_argument("--output", default="report.md", help="Where to write the triage report")
    parser.add_argument("--offline", action="store_true",
                        help="Fallback keyword decisions, no model")
    parser.add_argument("--github", default=None, metavar="OWNER/REPO",
                        help="Fetch open issues live from this GitHub repo instead of --input")
    parser.add_argument("--limit", type=int, default=10,
                        help="How many issues to fetch with --github (default 10)")
    parser.add_argument("--save-fetched", default="real_issues_live.json",
                        help="Where to save issues fetched with --github")
    parser.add_argument("--repo", default=None, metavar="OWNER/REPO",
                        help="Repo slug used to build issue links for JSON inputs without html_url")
    args = parser.parse_args()

    output_path = Path(args.output)
    repo = args.repo or args.github

    if args.github:
        try:
            issues = fetch_open_issues(args.github, limit=args.limit)
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        Path(args.save_fetched).write_text(
            json.dumps(issues, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        source = f"github:{args.github}"
        print(f"Fetched {len(issues)} open issue(s) from {args.github} "
              f"-> {args.save_fetched}")
    else:
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"Input file not found: {input_path}", file=sys.stderr)
            return 1
        issues = load_issues(input_path)
        source = str(input_path)

    if args.offline:
        return run_offline(issues, source, output_path, repo)
    return run_online(issues, source, output_path, repo)


if __name__ == "__main__":
    raise SystemExit(main())
