# TriageMinion

**TriageMinion is a GitHub issue triage agent built with the OpenMinion 0.1
Python SDK: the model itself classifies each issue — category, priority,
missing information — and a Markdown report is rendered from its recorded
decisions for a maintainer to review.**

Maintainers of busy open-source projects lose hours reading new issues.
TriageMinion does the first pass in seconds: it fetches or loads the open
issues, an OpenMinion agent classifies each one (bug / feature / docs /
security / question, priority P0–P3, suggested labels, what the reporter
left out), and the result is a draft report — nothing is written to any
repository unless a human takes the separate, explicit apply step.

> A simple agent that works reliably — that is the goal. No polished
> frontend, no multi-agent system, nothing the workflow does not need.

## How it works through OpenMinion

1. **Load or fetch** — issues come from a JSON file, or are fetched
   **live from GitHub** with `--github owner/repo` (public REST API,
   no token needed for reads).
2. **Tools** — three decorated `@tool` functions, exposed only for the
   run: `get_issue_page` (paged reads of the raw issues, 4 per call),
   `record_triage` (the model records each decision as structured,
   enum-validated data: category, priority, labels, missing info,
   one-line reason), and `save_report` (renders the report from the
   recorded decisions — and refuses to save while decisions are
   missing, telling the model which issue ids remain).
3. **Sessions / agent loop** — the agent runs with an explicit
   `session_id="triage-minion-demo"` inside a context-manager runtime
   lifecycle, with a per-run deadline (`timeout_seconds=300`) and typed
   failure handling (`ProviderError`, `TurnTimeoutError`).
4. **Provider** — any tool-capable model provider configured through
   OpenMinion; our verified runs use **OpenRouter** free models via the
   `openrouter` preset, key supplied only through the
   `OPENROUTER_API_KEY` environment variable.
5. **Permissions** — per-tool action-policy rules in
   `.openminion/agents.json` (`"mode": "auto"` for each of the three
   tools) so headless runs are not stalled by interactive policy
   confirmations (see BUILDING_BLOCKS.md for why this is needed).
6. **Diagnostics** — every run ends with validation of the recorded
   decisions against the input. Issues a model run failed to record
   are filled by the fallback rules and **disclosed** in the report's
   "Repaired entries" section; a run is never silently partial.

**The keyword classifier is a fallback, not the brain.** Deterministic
keyword rules (`triage.py`) exist only for the `--offline` mode and for
repairing incomplete model runs; decisions they produce are labelled
`fallback` in the report. In the online mode the model classifies —
that is the meaningful SDK usage. One renderer (`report.py`) serves the
online mode, the offline mode, and repairs — the format never changes,
and reports carry full untruncated titles with clickable issue links.

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
  SDK's HTTP client (`InvalidURL: Invalid port: ':1]'`); run with
  `NO_PROXY=localhost,127.0.0.1`.

## Reproduce

Run the tests first — they are fully offline and pin the expected
behaviour before any model is involved:

```bash
pip install -r requirements-dev.txt   # pytest, dev only
python -m pytest -q                   # 35 tests, fully offline
```

The suite covers the fallback classifier on all 16 known issues,
renderer links/full titles/exactly-once coverage, partial-report
repair, body-based environment detection, and GitHub fetch parsing
from a recorded fixture.

Then the runs:

```bash
# Real model-backed run on the sample issues
python app.py --input sample_issues.json --output report.md

# Fetch 10 open issues LIVE from a GitHub repo, then triage them
# (fetched issues saved to real_issues_live.json; GITHUB_TOKEN optional)
python app.py --github OpenMinion/openminion --limit 10 \
    --save-fetched real_issues_live.json --output report.md

# Offline run (fallback rules, deterministic — no key, no network)
python app.py --offline --input sample_issues.json --output report.md
```

## Evidence

Saved artifacts from real runs of the current design — open them and
check the agent's verdicts against the issues themselves:

- `report.live-model.md` — **live model run of the current model-led
  design** (2026-11-23) on the 10 newest OpenMinion issues
  (`real_issues_live.json`, #821–#803, fetched via the GitHub API).
  The model recorded **7 of 10 decisions itself**; the 3 it missed
  (#811, #805, #803) were repaired by the fallback rules and are
  disclosed in the report's "Repaired entries" section.
- `report.live-model-v3.md` — the run filmed for the demo video
  (2026-11-23). Free models are inconsistent: in this take the model
  recorded only 1 of 10 decisions before stopping, and the repair path
  filled the rest, again disclosed. Both reports are kept on purpose —
  the difference between them *is* the finding about free-model
  reliability.
- `report.real-issues.md` / `report.example.md` — offline fallback runs
  on the 10 real issues and the 6 samples (deterministic; the baseline
  the tests pin).
- `report.real-model.md` — kept unchanged as historical evidence of the
  2026-11-18 model run of the *previous* (facts-first) design;
  `archive/report.real-model.partial.md` is that design's truncated
  first attempt.
- **Live label/comment demo (2026-11-23):** `github_actions.py --apply`
  ran against this project's own repository and posted real labels and
  TriageMinion triage-summary comments — see
  [issue #1](https://github.com/Bidan11/triage-minion/issues/1)
  (crash report → `type:bug`, `priority:P1`) and
  [issue #2](https://github.com/Bidan11/triage-minion/issues/2)
  (dark-mode request), with the triage comment on each.

## Act on your own repo (optional)

```bash
# Plan only — prints labels + comments, writes nothing:
python github_actions.py Bidan11/triage-minion --input demo_issues.json

# Actually apply (token must belong to the repo owner, or it refuses):
GITHUB_TOKEN=... python github_actions.py Bidan11/triage-minion \
    --input demo_issues.json --apply
```

## Boundaries / safety

- **The agent never writes to other people's repositories.** Its
  GitHub reads are public-API reads; it has no write path to any repo
  it does not own.
- **Label/comment writes happen only on the owner's own repo** — the
  actions module verifies the token belongs to the repo owner and
  refuses otherwise — **and only with the explicit `--apply` flag**.
  The default is a dry-run plan that writes nothing.
- **Reports are drafts.** A maintainer reviews the triage report
  before any label is applied; the agent suggests, the human decides.
- API keys and tokens are supplied through environment variables only
  and are never stored in the repository.

Detailed findings — what worked, what did not, written as reproducible
mini bug reports — are in [BUILDING_BLOCKS.md](BUILDING_BLOCKS.md).
The short submission summary is in [BUIDL.md](BUIDL.md); submission
materials are in [SUBMISSION.md](SUBMISSION.md).

## Status

- [x] SDK 0.1.20 installed and imports verified
- [x] Offline workflow verified end to end (6 sample issues triaged)
- [x] Echo-provider run through the Agent runtime verified (wiring only —
      echo does not call tools or a model)
- [x] Real model-backed runs verified via OpenRouter, including a clean
      run on the 10 real issues under the previous design
      (`report.real-model.md`)
- [x] Public GitHub repository
- [x] Redesign after code review (2026-11-21): model-led classification
      via `record_triage`, live GitHub fetch (`--github`),
      own-repo actions module, unified renderer, partial-report
      repair, automated tests (35 passing, offline)
- [x] Live model run of the NEW model-led design (2026-11-23) —
      `report.live-model.md`: model recorded 7/10 decisions itself,
      3 repaired and disclosed
- [x] Label/comment demo applied live on our own repo via
      `github_actions.py --apply` (2026-11-23) — issues #1 and #2
- [x] Demo video recorded from a real model-backed run of the new
      design (2026-11-23)
- [ ] Submission PR to the organisers' Hackathon #5 repository
      (repository URL not yet announced by the organisers)

## License

MIT
