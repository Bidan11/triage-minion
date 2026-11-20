# TriageMinion

A small, working GitHub **issue triage agent** built with the **OpenMinion 0.1
Python SDK** for Cortensor Hackathon #5 (DoraHacks).

Maintainers of busy open-source projects lose hours reading new issues.
TriageMinion does the first pass in seconds: the model classifies each
issue (bug / feature / docs / security / question), assigns a priority
(P0–P3), notes what information is missing from the reporter, and a
Markdown triage report is rendered from its recorded decisions for a
maintainer to review before any label is applied.

> A simple agent that works reliably — that is the goal. No polished
> frontend, no multi-agent system, nothing the workflow does not need.

## How it works

1. **Load or fetch** — issues come from a JSON file, or are fetched
   **live from GitHub** with `--github owner/repo` (public REST API,
   no token needed for reads).
2. **The model classifies** — an OpenMinion `Agent` (explicit
   `session_id`) reads each issue's title and body through the paged
   `get_issue_page` tool and records its own decision for every issue
   through the structured `record_triage` tool: category, priority,
   suggested labels, missing information, and a one-line reason.
3. **One renderer** — `save_report` renders the report from the
   recorded decisions (full titles, clickable issue links). A single
   renderer (`report.py`) serves the online mode, the offline mode,
   and repairs — the format never changes.
4. **Repair, never silently partial** — after any run, decisions are
   validated against the input. Issues a model run failed to record
   are filled by the fallback rules and disclosed in the report.
5. **Human in control** — the report is a *draft*. Applying labels or
   comments to a repository is a separate step (`github_actions.py`:
   dry-run by default, owner's own repos only, explicit `--apply`).

**The keyword classifier is a fallback, not the brain.** Deterministic
keyword rules (`triage.py`) exist only for the `--offline` mode and
for repairing incomplete model runs; decisions they produce are
labelled `fallback` in the report. In the online mode the model
classifies — that is the meaningful SDK usage.

## Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt   # openminion==0.1.20

# Configure one real, tool-capable model provider (key stays in env vars):
openminion setup --no-chat
openminion doctor --check-turn
```

**Note on versions:** this project is built and tested with the OpenMinion
SDK **0.1.20** (pinned in `requirements.txt`), while the real issues in
`real_issues.json` come from the upstream OpenMinion **0.1.22** release
cycle — several are tagged `[0.1.22]`, and two were first reported on
0.1.21 and confirmed still present on 0.1.22.

Notes from our verified setup (OpenRouter, free model):

- `openminion setup --no-chat --provider openrouter --model cohere/north-mini-code:free`
  with `OPENROUTER_API_KEY` in the environment.
- Headless runs need the demo tools pre-approved, otherwise the
  runtime stops at an interactive policy confirmation. In
  `.openminion/agents.json`, add per-tool rules with `"mode": "auto"`
  for each tool name: `get_issue_page`, `record_triage`, `save_report`.
- In proxied sandboxes, bracketed IPv6 entries in `NO_PROXY` break the
  SDK's HTTP client (`Invalid port: ':1]'`); run with
  `NO_PROXY=localhost,127.0.0.1`.

## Run

```bash
# Real model-backed run (the hackathon demo path)
python app.py --input sample_issues.json --output report.md

# Fetch 10 open issues LIVE from a GitHub repo, then triage them
# (saved to real_issues_live.json; GITHUB_TOKEN optional for reads)
python app.py --github OpenMinion/openminion --limit 10 --output report.md

# Offline logic test (fallback rules, deterministic — for CI / verification)
python app.py --offline --input sample_issues.json --output report.md
```

Example output: see `report.example.md` (samples) and
`report.real-issues.md` (10 real OpenMinion issues).
`report.real-model.md` is kept **unchanged** as historical evidence of
the 2026-11-18 model run of the *previous* design (facts-first); the
current model-led design has not had its live run yet — it needs a
provider key (see Status).

## Act on your own repo (optional)

```bash
# Plan only — prints labels + comments, writes nothing:
python github_actions.py Bidan11/triage-minion --input sample_issues.json

# Actually apply (token must belong to the repo owner, or it refuses):
GITHUB_TOKEN=... python github_actions.py Bidan11/triage-minion \
    --input sample_issues.json --apply
```

## Tests

```bash
pip install -r requirements-dev.txt   # pytest, dev only
python -m pytest -q                   # 35 tests, fully offline
```

The suite covers the fallback classifier on all 16 known issues,
renderer links/full titles/exactly-once coverage, partial-report
repair, body-based environment detection, and GitHub fetch parsing
from a recorded fixture.

## OpenMinion building blocks used

- Decorated callable tools (`@tool`) exposed only for the run —
  including a **structured decision tool** (`record_triage`) whose
  records, not free text, drive the final report
- `forced_tools` so the demo always exercises the issue-page tool
- Explicit sessions (`session_id="triage-minion-demo"`)
- Context-manager runtime lifecycle (`with Agent(...)`)
- Typed failure handling: `ProviderError`, `TurnTimeoutError`
- Per-run deadline (`timeout_seconds=300`)
- Action-policy rules so the demo tools can run unattended

Detailed findings — what worked, what did not — are in
[BUILDING_BLOCKS.md](BUILDING_BLOCKS.md). Submission materials and the
demo outline are in [SUBMISSION.md](SUBMISSION.md).

## Status

- [x] SDK 0.1.20 installed and imports verified
- [x] Offline workflow verified end to end (6 sample issues triaged)
- [x] Echo-provider run through the Agent runtime verified (wiring only —
      echo does not call tools or a model)
- [x] Real model-backed run verified via OpenRouter
      (`cohere/north-mini-code:free`): model called both tools and saved
      its own report — see `report.model.md`
- [x] Public GitHub repository
- [x] Clean model run on the 10 real issues (facts tool paginates after a
      truncation finding; first attempt kept as
      `archive/report.real-model.partial.md`) — see `report.real-model.md`
- [x] Redesign after code review (2026-11-21): model-led classification
      via `record_triage`, live GitHub fetch (`--github`, verified —
      `real_issues_live.json`), own-repo actions module (dry-run
      verified), unified renderer, partial-report repair, automated
      tests (35 passing, offline)
- [ ] Live model run of the NEW model-led design — needs a provider
      key; not run yet
- [ ] Label/comment demo on our own repo via `github_actions.py
      --apply` — needs a GitHub token; not run yet (dry-run only)
- [ ] Demo video
- [ ] Submission PR to the organisers' Hackathon #5 repository

## License

MIT
