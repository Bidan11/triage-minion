# TriageMinion

**An OpenMinion agent that triages GitHub issues in seconds — the model
itself assigns each issue a category, a priority, and a note of what's
missing, and renders a draft report a maintainer can act on.**

## How it works

1. Issues are loaded from a JSON file or fetched **live from GitHub**
   (`--github owner/repo`, public REST API).
2. An OpenMinion `Agent` (explicit `session_id`, context-manager
   lifecycle) reads the raw issues through the paged `get_issue_page`
   tool — 4 issues per call.
3. The model classifies each issue **itself** and records every
   decision through the structured `record_triage` tool: category
   (bug / feature / docs / security / question), priority (P0–P3),
   suggested labels, missing information, one-line reason.
4. `save_report` renders the report from the recorded decisions (full
   titles, clickable links) — and refuses to save while any decision
   is missing. Gaps a model run leaves are filled by deterministic
   fallback rules and **disclosed** in a "Repaired entries" section.
5. A maintainer reviews the draft. Applying the suggested labels and a
   triage comment to a real repository is a separate step
   (`github_actions.py`): dry-run by default, owner's own repos only,
   explicit `--apply`.

## Features

- **Model-led classification via a structured decision tool** —
  `record_triage` records are enum-validated, so every report entry
  traces back to a decision with a reason (OpenMinion `@tool` +
  structured tool output).
- **Paged tool reads** — `get_issue_page` exists because a single
  10-issue tool result arrived truncated at the model; paging fixed it
  (OpenMinion tool-result handling, worked around in our tool design).
- **Headless-safe runs** — per-tool action-policy rules
  (`mode: "auto"` in `.openminion/agents.json`) so the agent runs
  unattended without interactive policy confirmations (OpenMinion
  permissions).
- **Validation + disclosed repair** — coverage is checked after every
  run; a partial model run is completed by labelled fallback decisions,
  never silently shipped (agent loop + our validation layer).
- **Live GitHub fetch and own-repo actions** — real issues in, real
  labels/comments out, with an ownership check before any write.
- **Provider-swappable** — verified on OpenRouter free models via the
  OpenMinion `openrouter` preset; typed errors (`ProviderError`,
  `TurnTimeoutError`) and a 300 s per-run deadline keep flaky free
  endpoints from crashing the workflow (OpenMinion providers).
- **Offline fallback + 35 tests** — `--offline` reproduces the report
  shape with no key and no network; the pytest suite pins the
  classifier, renderer, repair, and fetch parsing.

## Why it matters

The first pass over new issues — reading, sorting, asking for missing
information — is repetitive work maintainers do at 2 a.m. TriageMinion
shows a small OpenMinion agent doing that pass end to end on real
issues, with an auditable trail: a judge can open the saved report and
check every verdict against the issue it came from. It is deliberately
small and reliable rather than ambitious and partial — and honest about
its limits: free models sometimes stop early, so the repair path is
part of the product, not an embarrassment hidden from the report.

## Evidence

- Repo: https://github.com/Bidan11/triage-minion
- The run filmed for the current demo video (recorded 2026-11-24;
  model recorded 10/10 decisions itself, no repairs):
  `report.live-model-v4.md`
- Earlier live model runs of the current design:
  `report.live-model.md` (2026-11-23; model 7/10, 3 repaired,
  disclosed) and `report.live-model-v3.md` (2026-11-23, an earlier
  filmed take; model 1/10 before stopping, repair disclosed) — the
  contrast between the reports is the free-model reliability
  finding, kept on purpose
- Offline baselines: `report.real-issues.md` (10 real OpenMinion
  issues), `report.example.md` (6 samples)
- Label/comment demo applied live on our own repo (2026-11-23):
  [issue #1](https://github.com/Bidan11/triage-minion/issues/1) and
  [issue #2](https://github.com/Bidan11/triage-minion/issues/2) carry
  real TriageMinion labels and triage-summary comments
- Tests: `python -m pytest -q` — 35 passing, fully offline
- Findings, written as reproducible mini bug reports:
  [BUILDING_BLOCKS.md](BUILDING_BLOCKS.md)
