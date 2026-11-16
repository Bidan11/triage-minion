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

Notes from our verified setup (OpenRouter, free model):

- `openminion setup --no-chat --provider openrouter --model cohere/north-mini-code:free`
  with `OPENROUTER_API_KEY` in the environment.
- Headless runs need the two demo tools pre-approved, otherwise the
  runtime stops at an interactive policy confirmation. In
  `.openminion/agents.json`, add per-tool rules:
  `{"match": {"tool_name": "get_triage_facts"}, "mode": "auto"}` and the
  same for `save_report`.
- In proxied sandboxes, bracketed IPv6 entries in `NO_PROXY` break the
  SDK's HTTP client (`Invalid port: ':1]'`); run with
  `NO_PROXY=localhost,127.0.0.1`.

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
- [ ] Clean model run on the 10 real issues (compact-facts fix applied;
      first attempt kept as `report.real-model.partial.md`) + demo video
- [ ] Submission PR to the organisers' Hackathon #5 repository

## License

MIT
