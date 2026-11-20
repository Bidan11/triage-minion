"""
Act on triage decisions in the OWNER'S OWN repository (fix 2b).

Given triage decisions for issues in one repository, this module can:

* apply the suggested labels to each issue, and
* post one triage-summary comment per issue.

Safety rules (non-negotiable):

* **Dry-run by default.** Nothing is written unless ``--apply`` is
  passed explicitly; a dry run only prints the plan.
* **Own repos only.** With ``--apply``, the token's owner (``GET
  /user``) must match the repository owner, otherwise the run refuses
  before any write.
* The token comes from the ``GITHUB_TOKEN`` environment variable and
  is never printed or stored.

Usage:
    # Plan only (no writes, token optional):
    python github_actions.py Bidan11/triage-minion --input issues.json

    # Actually apply labels + comments (token required):
    GITHUB_TOKEN=... python github_actions.py Bidan11/triage-minion \
        --input issues.json --apply

Decisions come from the fallback classifier by default, or from a
decisions JSON file (``--decisions``) recorded by a model run.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from github_client import _request, fetch_authenticated_login
from triage import classify_issue

LABEL_COLORS = {
    "type:bug": "d73a4a",
    "type:feature": "a2eeef",
    "type:docs": "0075ca",
    "type:security": "b60205",
    "type:question": "d876e3",
    "priority:P0": "b60205",
    "priority:P1": "d93f0b",
    "priority:P2": "fbca04",
    "priority:P3": "0e8a16",
}


def check_ownership(repo_owner: str, token_login: str) -> bool:
    """True when the token belongs to the repository's owner."""
    return repo_owner.lower() == token_login.lower()


def comment_body(decision: dict) -> str:
    missing = ", ".join(decision.get("missing_info") or []) or "nothing — report looks complete"
    labels = ", ".join(decision.get("suggested_labels") or []) or "-"
    return (
        "TriageMinion triage summary\n\n"
        f"- Category: {decision['category']}\n"
        f"- Priority: {decision['priority']}\n"
        f"- Missing info: {missing}\n"
        f"- Suggested labels: {labels}\n"
        f"- Why: {decision.get('reason', '')}\n\n"
        "_Draft by TriageMinion — a maintainer should confirm before acting._"
    )


def plan_actions(decisions: list[dict]) -> list[dict]:
    """The write plan: one entry per issue with labels + comment text.
    Pure function — no network — so dry runs and tests use it directly."""
    return [
        {
            "issue": d["id"],
            "labels": list(d.get("suggested_labels") or []),
            "comment": comment_body(d),
        }
        for d in decisions
    ]


def _ensure_label(repo: str, name: str, token: str) -> None:
    status, _ = _request(
        f"/repos/{repo}/labels",
        token=token,
        method="POST",
        payload={"name": name, "color": LABEL_COLORS.get(name, "cccccc")},
    )
    if status not in (201, 422):  # 422 = label already exists
        raise RuntimeError(f"Creating label {name!r} failed with {status}")


def apply_actions(repo: str, actions: list[dict], token: str) -> list[str]:
    """Execute the plan. Returns human-readable result lines."""
    results = []
    ensured: set[str] = set()
    for action in actions:
        for label in action["labels"]:
            if label not in ensured:
                _ensure_label(repo, label, token)
                ensured.add(label)
        status, _ = _request(
            f"/repos/{repo}/issues/{action['issue']}/labels",
            token=token, method="POST", payload={"labels": action["labels"]},
        )
        if status not in (200, 201):
            raise RuntimeError(
                f"Applying labels to #{action['issue']} failed with {status}"
            )
        status, _ = _request(
            f"/repos/{repo}/issues/{action['issue']}/comments",
            token=token, method="POST", payload={"body": action["comment"]},
        )
        if status != 201:
            raise RuntimeError(
                f"Posting comment on #{action['issue']} failed with {status}"
            )
        results.append(f"#{action['issue']}: labels {action['labels']} + comment posted")
    return results


def load_decisions(input_path: Path, decisions_path: Path | None,
                   repo: str) -> list[dict]:
    issues = json.loads(input_path.read_text(encoding="utf-8"))
    if decisions_path:
        recorded = json.loads(decisions_path.read_text(encoding="utf-8"))
        by_id = {d.get("id"): d for d in recorded}
        return [by_id[i["id"]] for i in issues if i.get("id") in by_id]
    return [classify_issue(i, repo=repo) for i in issues]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Apply TriageMinion labels/comments to your own repo (dry-run by default)"
    )
    parser.add_argument("repo", help="owner/repo — must be your own repository")
    parser.add_argument("--input", default="sample_issues.json",
                        help="JSON file with the repo's issues")
    parser.add_argument("--decisions", default=None,
                        help="Optional decisions JSON recorded by a model run")
    parser.add_argument("--apply", action="store_true",
                        help="Actually write to GitHub (default: dry-run plan only)")
    args = parser.parse_args()

    if "/" not in args.repo:
        print("Repo must look like owner/repo.", file=sys.stderr)
        return 2
    owner = args.repo.split("/", 1)[0]

    decisions = load_decisions(Path(args.input),
                               Path(args.decisions) if args.decisions else None,
                               args.repo)
    actions = plan_actions(decisions)

    token = os.environ.get("GITHUB_TOKEN")
    if args.apply:
        if not token:
            print("--apply requires GITHUB_TOKEN in the environment.", file=sys.stderr)
            return 2
        login = fetch_authenticated_login(token)
        if not check_ownership(owner, login):
            print(
                f"Refusing to write: token belongs to {login!r}, but the repo "
                f"owner is {owner!r}. Actions only run on your own repositories.",
                file=sys.stderr,
            )
            return 2
        print(f"Ownership verified: {login} owns {args.repo}. Applying...")
        for line in apply_actions(args.repo, actions, token):
            print(" ", line)
        return 0

    print(f"DRY RUN — no writes will be made to {args.repo}.")
    if token:
        login = fetch_authenticated_login(token)
        ok = check_ownership(owner, login)
        print(f"Token owner: {login} — ownership check: {'PASS' if ok else 'FAIL'}")
    else:
        print("No GITHUB_TOKEN set: ownership not verified (fine for a dry run).")
    for action in actions:
        print(f"\n#{action['issue']}: add labels {action['labels']}")
        print("  comment:")
        for line in action["comment"].splitlines():
            print(f"    {line}")
    print(f"\n{len(actions)} issue(s) planned. Re-run with --apply to write.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
