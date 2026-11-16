"""
TriageMinion - a GitHub issue triage agent built on the OpenMinion 0.1 Python SDK.

Workflow (one useful, repeatable job):
  1. Load a list of GitHub issues (JSON export or the bundled sample file).
  2. The agent classifies each issue: category, priority, missing information.
  3. It drafts a triage report (Markdown) a maintainer can act on directly.
  4. Saving the report is a separate, explicit step so a human stays in control.

Run modes:
  * Online (hackathon demo): uses a real model through OpenMinion.
        python app.py --input sample_issues.json --output report.md
    Requires the OpenMinion SDK and a configured model-provider key
    (see README, "Setup").
  * Offline (logic test): deterministic rule-based triage, no model needed.
    Useful for CI and for verifying the workflow end to end.
        python app.py --offline --input sample_issues.json --output report.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Deterministic triage logic (shared by the offline mode and used by the
# online agent's tools so the model works from verified facts, not guesses).
# ---------------------------------------------------------------------------

CATEGORY_SIGNALS = {
    "bug": [
        "error", "crash", "fails", "broken", "bug", "exception", "500",
        "regression", "cannot", "never applied", "wedge", "stuck", "incorrect",
    ],
    "security": ["vulnerability", "xss", "sql injection", "token exposed", "security issue"],
    "feature": ["feature", "add support", "add ", "would be nice", "request", "enhancement", "proposal"],
    "docs": ["docs", "documentation", "readme", "typo", "example"],
    "question": ["how do", "how to", "question", "help", "?"],
}

PRIORITY_SIGNALS = {
    "P0": ["vulnerability", "token exposed", "data loss", "all users", "production down"],
    "P1": ["crash", "regression", "500", "cannot login", "broken after"],
    "P2": ["fails", "error", "slow", "sometimes", "cannot"],
}


def classify_issue(issue: dict) -> dict:
    title = issue.get("title", "").lower()
    body = issue.get("body", "").lower()
    text = f"{title} {body}"

    # Title signals weigh double: the title states the reporter's intent,
    # while a body can mention risky words in passing (a feature proposal
    # about preventing leaks is not itself a security incident).
    scores = {}
    for name, signals in CATEGORY_SIGNALS.items():
        scores[name] = sum(2 for s in signals if s in title) + sum(
            1 for s in signals if s in body
        )
    # A structured bug report is a strong signal on its own.
    if "steps to reproduce" in text or "step to reproduce" in text:
        scores["bug"] += 3

    category = "needs-info"
    best_hits = 0
    for name, hits in scores.items():
        if hits > best_hits:
            category, best_hits = name, hits
    # A strong security phrase in the title is decisive, even when the
    # reporter also asks a question in the body ("token exposed ... how do
    # I rotate it?" is a security report first, a question second).
    if any(s in title for s in CATEGORY_SIGNALS["security"]):
        category = "security"

    priority = "P3"
    for level in ("P0", "P1", "P2"):
        if any(s in text for s in PRIORITY_SIGNALS[level]):
            priority = level
            break

    has_version = bool(
        re.search(r"\d+\.\d+\.\d+", text) or "version" in text or "environment" in text
    )
    has_steps = bool(re.search(r"steps|reproduce|expected", text))
    missing = []
    if not has_version and category in ("bug", "security"):
        missing.append("version / environment")
    if not has_steps and category in ("bug", "security"):
        missing.append("reproduction steps")

    return {
        "id": issue.get("id"),
        "title": issue.get("title", "(untitled)"),
        "category": category,
        "priority": priority,
        "missing_info": missing,
        "suggested_label": f"type:{category}",
    }


def build_report(results: list[dict], source: str) -> str:
    lines = [
        "# Triage Report",
        "",
        f"Source: `{source}` - {len(results)} issue(s) triaged.",
        "",
        "| # | Issue | Category | Priority | Missing info | Suggested label |",
        "|---|-------|----------|----------|--------------|-----------------|",
    ]
    for r in results:
        missing = ", ".join(r["missing_info"]) if r["missing_info"] else "-"
        title = str(r["title"]).replace("|", "/")
        lines.append(
            f"| {r['id']} | {title} | {r['category']} | {r['priority']} | {missing} | `{r['suggested_label']}` |"
        )
    lines += ["", "Next step: a maintainer reviews this draft before any label is applied.", ""]
    return "\n".join(lines)


def load_issues(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Issue file must be a JSON list of issues.")
    return data


# ---------------------------------------------------------------------------
# Online mode: OpenMinion agent with run-scoped tools.
# ---------------------------------------------------------------------------

def run_online(input_path: Path, output_path: Path) -> int:
    try:
        from openminion import Agent, ProviderError, TurnTimeoutError, tool
    except ImportError:
        print(
            "OpenMinion SDK is not installed. Run: pip install -r requirements.txt\n"
            "Or test the workflow without a model: python app.py --offline",
            file=sys.stderr,
        )
        return 2

    issues = load_issues(input_path)
    facts = [classify_issue(i) for i in issues]

    @tool
    def get_triage_facts() -> str:
        """Return the verified, deterministic triage facts for the loaded issues."""
        # Compact payload: long issue titles and pretty-printing can push the
        # tool result past the runtime's truncation limit on larger sets.
        compact = [
            {**f, "title": (f["title"][:117] + "...") if len(f["title"]) > 120 else f["title"]}
            for f in facts
        ]
        return json.dumps(compact)

    @tool
    def save_report(markdown: str) -> str:
        """Save the final triage report to the output file chosen by the operator."""
        output_path.write_text(markdown, encoding="utf-8")
        return f"Saved report to {output_path}"

    instructions = (
        "You are TriageMinion, an issue triage assistant for open-source maintainers. "
        "Call get_triage_facts first and base every claim on those facts only. "
        "Copy each issue's category and priority from the facts exactly; never "
        "re-classify an issue yourself. "
        "Write a short, clear triage report in Markdown: a summary table, the top "
        "priority items first, and what information is missing from reporters. "
        "Then call save_report with the finished report. Do not invent issues, "
        "versions, or error messages that are not in the facts."
    )

    try:
        with Agent(
            instructions=instructions,
            tools=[get_triage_facts, save_report],
            forced_tools=["get_triage_facts"],
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

    if not output_path.exists():
        # Fall back to the deterministic report so the run always leaves evidence.
        output_path.write_text(build_report(facts, str(input_path)), encoding="utf-8")
        print("Note: wrote the deterministic report as run evidence.")
    return 0


def run_offline(input_path: Path, output_path: Path) -> int:
    issues = load_issues(input_path)
    results = [classify_issue(i) for i in issues]
    output_path.write_text(build_report(results, str(input_path)), encoding="utf-8")
    print(f"Triaged {len(results)} issue(s) -> {output_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="TriageMinion - OpenMinion issue triage agent")
    parser.add_argument("--input", default="sample_issues.json", help="JSON file with issues")
    parser.add_argument("--output", default="report.md", help="Where to write the triage report")
    parser.add_argument("--offline", action="store_true", help="Deterministic test mode, no model")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    if not input_path.exists():
        print(f"Input file not found: {input_path}", file=sys.stderr)
        return 1

    if args.offline:
        return run_offline(input_path, output_path)
    return run_online(input_path, output_path)


if __name__ == "__main__":
    raise SystemExit(main())
