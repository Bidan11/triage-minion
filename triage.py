"""
Fallback triage rules for TriageMinion.

IMPORTANT — this module is a FALLBACK, not the product's brain:

* In the online (OpenMinion SDK) mode, the **model** classifies every
  issue itself and records its decisions through the ``record_triage``
  tool (see ``app.py``).
* This deterministic keyword classifier is used only when no model is
  available: the ``--offline`` mode, and the repair step that fills in
  any issue a model run failed to record (such fills are labelled
  ``decided_by="fallback"`` in the report).

The rules were hardened after a review found the original version too
fragile (see BUILDING_BLOCKS.md): a bare "add " no longer forces
``feature``, a bare "?" no longer forces ``question``, a bare "500" no
longer forces ``P1``, and the word "security" alone no longer forces
the ``security`` category — that requires strong evidence such as a
vulnerability, a CVE reference, an exploit, or exposed credentials.
"""

from __future__ import annotations

import re

CATEGORIES = ("bug", "feature", "docs", "security", "question")
PRIORITIES = ("P0", "P1", "P2", "P3")

# Scored keyword signals. Deliberately conservative: single weak words
# ("add", "?", "500", "security") are NOT in these lists on their own.
CATEGORY_SIGNALS = {
    "bug": [
        "error", "crash", "fails", "failed", "broken", "bug", "exception",
        "regression", "cannot", "never applied", "wedge", "stuck",
        "incorrect", "not working",
    ],
    "security": [
        "vulnerability", "security", "xss", "sql injection",
        "token exposed", "exploit",
    ],
    "feature": [
        "feature", "add support", "would be nice", "request",
        "enhancement", "proposal",
    ],
    "docs": ["docs", "documentation", "readme", "typo"],
    "question": ["how do", "how to", "question", "help"],
}

# Strong security evidence: any one of these (title or body) is enough
# to call an issue `security` even when other signals compete — e.g.
# "API token exposed ... how do I rotate it?" is a security report
# first and a question second. A bare mention of the word "security"
# (a feature request *about* a security settings page) is not enough.
STRONG_SECURITY_SIGNALS = [
    "vulnerability", "cve-", "exploit", "token exposed",
    "api key exposed", "password exposed", "password leaked",
    "credentials leaked", "secret leaked", "security leak",
    "sql injection", "xss", "auth bypass", "bypass authentication",
    "privilege escalation", "unauthenticated access",
]

PRIORITY_SIGNALS = {
    "P0": [
        "vulnerability", "token exposed", "data loss", "all users",
        "production down",
    ],
    "P1": ["crash", "regression", "cannot login", "broken after"],
    "P2": ["fails", "error", "slow", "sometimes", "cannot"],
}

# An HTTP 500 only signals P1 in an error context — "fails with a 500
# error", "HTTP 500", "internal server error". A bare "500" (500 users,
# 500 items) must not.
_HTTP_500_ERROR = re.compile(
    r"(\b500\b[^.\n]{0,24}\berror\b|\berror\b[^.\n]{0,24}\b500\b"
    r"|http\D{0,3}500|internal server error)",
    re.IGNORECASE,
)

# Environment / version evidence. Judged from the issue BODY only
# (fix 7): a version tag in the title ("[0.1.22] ...") says where the
# reporter filed the issue, not that they provided their environment.
_ENV_PATTERNS = [
    r"\benvironment\b",
    r"\bversion\b\s*[:\-]",
    r"\bversion\b[^.\n]{0,30}\d+\.\d+",
    r"\d+\.\d+\.\d+",
    r"\bpython\s*3\.\d+",
    r"\bnode\.?js?\s*v?\d+",
    r"\boperating system\b",
    r"\bos\s*[:\-]",
    r"\bwindows\s*\d+",
    r"\bmacos\b",
    r"\blinux\b",
    r"\bubuntu\b",
    r"\bandroid\s*\d+",
]

_STEP_PATTERNS = [
    r"steps to reproduce",
    r"step to reproduce",
    r"reproduction steps",
    r"\breproduc",  # reproduce / reproduced / reproducible
    r"\bexpected\b",
]


def reporter_provided_environment(issue: dict) -> bool:
    """True when the issue BODY carries version/environment evidence.

    The title is never consulted: a "[0.1.22]" title tag is the release
    the issue was filed against, not the reporter's environment.
    """
    body = issue.get("body", "") or ""
    return any(re.search(p, body, re.IGNORECASE) for p in _ENV_PATTERNS)


def reporter_provided_steps(issue: dict) -> bool:
    """True when the issue BODY mentions reproduction steps / expected
    behaviour."""
    body = issue.get("body", "") or ""
    return any(re.search(p, body, re.IGNORECASE) for p in _STEP_PATTERNS)


def missing_info_for(issue: dict, category: str) -> list[str]:
    """What a maintainer still needs from the reporter (bugs/security)."""
    missing = []
    if category in ("bug", "security"):
        if not reporter_provided_environment(issue):
            missing.append("version / environment")
        if not reporter_provided_steps(issue):
            missing.append("reproduction steps")
    return missing


def issue_url(issue: dict, repo: str | None = None) -> str | None:
    """Best-known web URL for an issue: the API's html_url when present,
    otherwise constructed from a known ``owner/repo`` slug."""
    url = issue.get("html_url") or issue.get("url")
    # The REST API's "url" field is an api.github.com URL, not the web
    # page; only html_url (or a constructed link) is clickable for a
    # human. api.github.com URLs contain "/repos/" after the host.
    if url and "api.github.com/repos/" in url:
        url = None
    if url:
        return url
    if repo and issue.get("id") is not None:
        return f"https://github.com/{repo}/issues/{issue['id']}"
    return None


def classify_issue(issue: dict, repo: str | None = None) -> dict:
    """Fallback keyword classification. Returns a decision dict in the
    same shape the model records through ``record_triage``."""
    title = (issue.get("title") or "").lower()
    body = (issue.get("body") or "").lower()
    text = f"{title} {body}"

    # Title signals weigh double: the title states the reporter's
    # intent, while a body can mention risky words in passing (a
    # feature proposal about *preventing* leaks is not itself a
    # security incident).
    scores = {name: 0 for name in CATEGORY_SIGNALS}
    matched: dict[str, list[str]] = {name: [] for name in CATEGORY_SIGNALS}
    for name, signals in CATEGORY_SIGNALS.items():
        for s in signals:
            if s in title:
                scores[name] += 2
                matched[name].append(f"'{s}' in title")
            if s in body:
                scores[name] += 1
                matched[name].append(f"'{s}' in body")
    # Structural signals: a "steps to reproduce" section is a bug
    # report; an explicit "feature request" is a feature.
    if any(p in body for p in ("steps to reproduce", "step to reproduce")):
        scores["bug"] += 3
        matched["bug"].append("'steps to reproduce' section")
    if "feature request" in body:
        scores["feature"] += 3
        matched["feature"].append("'feature request' in body")

    category = "needs-info"
    best_hits = 0
    for name in CATEGORY_SIGNALS:
        if scores[name] > best_hits:
            category, best_hits = name, scores[name]

    # Strong security evidence overrides competing weak signals.
    strong = next((s for s in STRONG_SECURITY_SIGNALS if s in text), None)
    if strong:
        category = "security"
        matched["security"].append(f"strong signal '{strong}'")

    priority = "P3"
    for level in ("P0", "P1", "P2"):
        if any(s in text for s in PRIORITY_SIGNALS[level]):
            priority = level
            break
        if level == "P1" and _HTTP_500_ERROR.search(text):
            priority = "P1"
            break

    signals = matched.get(category, [])[:3]
    reason = "Keyword fallback"
    if signals:
        reason += ": " + "; ".join(signals)
    if category == "needs-info":
        reason = "Keyword fallback: no category signal matched"

    return {
        "id": issue.get("id"),
        "title": issue.get("title", "(untitled)"),
        "url": issue_url(issue, repo),
        "category": category,
        "priority": priority,
        "missing_info": missing_info_for(issue, category),
        "suggested_labels": [f"type:{category}", f"priority:{priority}"],
        "reason": reason,
        "decided_by": "fallback",
    }
