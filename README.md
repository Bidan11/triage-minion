# TriageMinion

A small, working GitHub **issue triage agent** built with the **OpenMinion 0.1
Python SDK** for Cortensor Hackathon #5 (DoraHacks).

Maintainers of busy open-source projects lose hours reading new issues.
TriageMinion does the first pass in seconds: it classifies each issue
(bug / feature / docs / security / question), assigns a priority (P0–P3),
notes what information is missing from the reporter, and drafts a Markdown
triage report a maintainer can review before any label is applied.

> A simple agent that works reliably — that is the goal. No polished
> frontend, no multi-agent system, nothing the workflow does not need.

## How it works

1. **Load** — issues come from a JSON file (a GitHub export, or the bundled
   `sample_issues.json` with 6 realistic issues).
2. **Facts first** — deterministic code computes category/priority signals.
   The model never has to guess these facts; it reads them through a tool.
3. **Agent run** — an OpenMinion `Agent` (explicit `session_id`) calls the
   `get_triage_facts` tool (`forced_tools` for the demo run), writes the
   report in its own words, and calls `save_report`.
4. **Human in control** — the report is a *draft*. A maintainer reviews it
   before any label is applied to a real repository.

## Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt   # openminion==0.1.20

# Configure one real, tool-capable model provider (key stays in env vars):
openminion setup --no-chat
openminion doctor --check-turn
```

## Run

```bash
# Real model-backed run (the hackathon demo path)
python app.py --input sample_issues.json --output report.md

# Offline logic test (no model, deterministic — for CI / verification)
python app.py --offline --input sample_issues.json --output report.md
```

Example output: see `report.example.md`.

## OpenMinion building blocks used

- Decorated callable tools (`@tool`) exposed only for the run
- `forced_tools` so the demo always exercises the facts tool
- Explicit sessions (`session_id="triage-minion-demo"`)
- Context-manager runtime lifecycle (`with Agent(...)`)
- Typed failure handling: `ProviderError`, `TurnTimeoutError`
- Per-run deadline (`timeout_seconds=120`)

Detailed findings — what worked, what did not — are in
[BUILDING_BLOCKS.md](BUILDING_BLOCKS.md). Submission materials and the
demo outline are in [SUBMISSION.md](SUBMISSION.md).

## Status

- [x] SDK 0.1.20 installed and imports verified
- [x] Offline workflow verified end to end (6 sample issues triaged)
- [x] Echo-provider run through the Agent runtime verified (wiring only —
      echo does not call tools or a model)
- [ ] Real model-backed run with a tool-capable provider (demo recording)
- [ ] Public GitHub repository + submission PR

## License

MIT
