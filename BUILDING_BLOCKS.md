# Building Blocks Tested — TriageMinion

For Cortensor Hackathon #5. Honest notes: verified facts only, updated as
testing continues.

## Used and verified (2026-11-16)

| Building block | How we used it | Result |
|---|---|---|
| Python SDK install | `pip install openminion==0.1.20` in a fresh venv (Python 3.12) | Works. The documented import check (`Agent, ProviderError, TurnTimeoutError, tool`, `openminion.api` types) passes. |
| Decorated tools | `@tool` on `get_triage_facts` and `save_report`, passed via `tools=[...]` | Registered as documented; exposed only for the run. |
| Sessions | Explicit `session_id="triage-minion-demo"` | Run completes inside the named session; session id is returned on the result. |
| Runtime lifecycle | `with Agent(...) as agent:` context manager | Runtime closes cleanly at the end of the run, no hanging process. |
| Echo provider | `openminion config init --provider echo`, then a full app run | Run completes and our fallback writes run evidence. **Finding:** echo only repeats the prompt — it cannot prove model-selected tool use, exactly as the docs warn. A tool-capable provider is required for the real demo. |
| Error types | `ProviderError` / `TurnTimeoutError` imported and handled in `app.py` | Imports verified; live provider-failure behaviour still to be exercised. |

## Design decision worth reporting

The model is **not** trusted to classify issues from scratch. Deterministic
code computes category/priority facts first, and the agent must read them
through the facts tool (`forced_tools=["get_triage_facts"]`). This made the
demo reproducible: the same input always produces the same facts, and the
model's job is limited to summarising and prioritising — the part it is
actually good at.

## Real-issues test — classifier iteration (2026-11-16)

We ran the deterministic classifier against 10 **real** open issues fetched
from the OpenMinion GitHub repository itself (`real_issues.json`), not just
our hand-written samples. The first version failed in instructive ways:

- A feature proposal for a `config diff` command was classified
  **security / P0**, because its body happened to contain the words
  "credentials leak" (it was proposing a tool to *prevent* leaks).
- Several genuine bug reports (handoff limits, telemetry, turn-input
  handling) fell through to `needs-info / P3`, because maintainer-written
  titles use technical wording with none of our original keywords.

Fixes applied in `classify_issue`:

1. **Title-weighted scoring** — title signals count double; the title
   states the reporter's intent, the body can mention risky words in
   passing.
2. **Strong-phrase override** — a decisive security phrase in the title
   ("token exposed", "vulnerability", ...) forces `security` even if the
   body also asks a question.
3. **Structured-report bonus** — a "steps to reproduce" section is treated
   as a strong bug-report signal, and version/environment detection now
   recognises version numbers and an "Environment" section.

After the fixes, re-verified 2026-11-16: **all 10 real issues classify
correctly** (8 bug, 2 feature — issues 767 and 759) and **all 6 sample
issues classify correctly**, including sample 104 as security / P0.
Reports: `report.real-issues.md`, `report.example.md`.

Honest limit: a keyword classifier is a **demo aid**, not the product. It
exists so the demo is reproducible and the model starts from verified
facts. In the online run the model does the final summarisation and
prioritisation in its own words, and a maintainer reviews the draft
before anything is applied.

## Still to test

- Real model-backed run (tool calling + report quality) with a tool-capable
  provider, incl. Cortensor Portal if access is granted.
- `save_report` tool being called by the model (vs. our deterministic
  fallback) and how often the model skips it.
- Behaviour on a large issue list (100+ issues): turn timeouts, context
  limits, and whether chunking per session is needed.
- Approval flow for a "dangerous" tool variant of `save_report`.

## What we learned (draft)

1. Pinning `openminion==0.1.20` in `requirements.txt` matters — the public
   API surface is version-specific and the quickstart is written against it.
2. The echo provider is a good wiring check but a misleading demo: it looks
   like a run happened while no tool was ever called. Our app therefore
   labels its fallback output instead of pretending the model produced it.
3. Facts-first tool design removes most prompt-engineering fragility from a
   triage workflow.
