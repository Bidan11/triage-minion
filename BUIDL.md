# TriageMinion

**Tagline:** An OpenMinion agent that triages GitHub issues in seconds —
category, priority, and what's missing — so maintainers can act, not read.

**Status (honest):** The original design was verified end to end in a
**real model-backed run via OpenRouter** (`report.real-model.md`, 10
real issues). After a code review, the project was redesigned
(2026-11-21): the model now classifies the issues itself and records
structured decisions, issues can be fetched live from GitHub, and an
actions module can label/comment on the owner's own repo. The redesign
is verified offline (35 tests), via a live GitHub fetch, and by
dry-run; **its live model run and the label/comment demo still need
the owner's keys and have not been run yet.**

## The problem

Busy open-source projects receive more issues than maintainers can read.
New issues arrive unlabelled, with mixed quality: some are critical
security reports, some are feature ideas, some are missing the version or
the steps to reproduce. The first pass — reading, sorting, asking for
missing information — is repetitive, slow, and easy to get wrong at 2 a.m.

## The solution

TriageMinion does that first pass as one small, repeatable workflow:

1. It loads a list of GitHub issues — or fetches them **live from
   GitHub** with `--github owner/repo`.
2. An OpenMinion agent reads each issue's title and body through a
   paged tool and **classifies it itself**: category (bug / feature /
   docs / security / question), priority (P0–P3), suggested labels,
   what information is missing, and a one-line reason — recording
   every decision through a structured `record_triage` tool.
3. The report is rendered from those recorded decisions (full titles,
   clickable links, top priorities first). If a run ends incomplete,
   the gaps are filled by fallback keyword rules and disclosed —
   never silently shipped as a partial report.
4. A maintainer reviews the draft. Applying labels/comments to a real
   repository is a separate, explicit step (`github_actions.py`,
   dry-run by default, owner's own repos only).

The output is a report like `report.example.md` (6 sample issues) and
`report.real-issues.md` (10 real open issues from the OpenMinion
repository itself: 8 bug, 2 feature).

## How it works

- `app.py` — CLI and the agent run: three `@tool` functions
  (`get_issue_page`, `record_triage`, `save_report`).
- `triage.py` — the keyword classifier, now an explicitly labelled
  **fallback** (offline mode + repair filler), hardened against the
  classic keyword traps (a bare "add"/"?"/"500" no longer decides
  anything; "security" needs strong evidence).
- `report.py` — the single renderer + validation/repair used by every
  mode, so the report format never changes.
- `github_client.py` / `github_actions.py` — live issue fetching and
  the own-repo label/comment actions.
- The agent is constructed with an explicit `session_id`, the
  issue-page tool is forced for the demo run
  (`forced_tools=["get_issue_page"]`), and the runtime is managed with
  a context manager. Provider and timeout failures surface as typed
  errors (`ProviderError`, `TurnTimeoutError`), deadline 300 s.
- `--offline` mode runs the same workflow with fallback decisions, so
  anyone can reproduce the report shape with no key and no network.
- 35 offline pytest tests pin the behaviour (see README).

Design choice worth noting: the model **is** trusted to classify —
that is the agent's job — but it must record each decision as
structured tool output. That makes a model run auditable: every entry
in the report traces back to a recorded decision with a reason, and
an incomplete run can be detected and repaired mechanically.

## OpenMinion building blocks used

- Python SDK **0.1.20** (pinned in `requirements.txt`), `Agent` facade
- Decorated callable tools (`@tool`), exposed only for the run
- `forced_tools` for a guaranteed tool call in the demo
- Explicit sessions (`session_id="triage-minion-demo"`)
- Context-manager runtime lifecycle
- Typed failure handling: `ProviderError`, `TurnTimeoutError`
- Per-run deadline (`timeout_seconds=300`)
- Echo provider for a credential-free wiring check
- Action-policy rules (`mode: "auto"` per tool) so headless runs are not
  blocked by interactive confirmations

Full findings, including what did not work: [BUILDING_BLOCKS.md](BUILDING_BLOCKS.md).

## What we learned

1. **The echo provider is a misleading demo.** A run "completes" while no
   tool is ever called. Our app labels its fallback output instead of
   pretending the model produced it — and the real demo must use a
   tool-capable provider.
2. **Naive keyword classification fails on real issues.** Tested against
   10 real OpenMinion issues, v1 called a feature proposal a security
   incident (its body mentioned "credentials leak") and missed several
   real bug reports. Title-weighted scoring, a strong-evidence security
   override, and a "steps to reproduce" bonus fixed all 10 — one more
   reason the keyword rules are now only a fallback behind the model,
   with their remaining traps pinned by regression tests.
3. **Pinning the SDK version matters.** The public API surface is
   version-specific; `openminion==0.1.20` in `requirements.txt` is what
   the code and docs are verified against.

## Demo

A ~3-minute demo outline (live run, report walkthrough, one honest
finding) is in [SUBMISSION.md](SUBMISSION.md#demo-outline-target-3-minutes).
The video will show a real model-backed run of the current model-led
design; that run is still to be recorded once a provider key is
available (the previous design's verified run is `report.real-model.md`).
