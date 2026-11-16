# TriageMinion

**Tagline:** An OpenMinion agent that triages GitHub issues in seconds —
category, priority, and what's missing — so maintainers can act, not read.

**Status (honest):** Verified end to end — offline, through an
echo-provider run, and in a **real model-backed run via OpenRouter**
(`cohere/north-mini-code:free`): the model called the facts tool, wrote
the report in its own words and saved it via the save tool
(`report.model.md`, 6 sample issues). A first model run on the 10 real
issues exposed a tool-result truncation (kept as
`report.real-model.partial.md`); the compact-facts fix is in and a clean
re-run follows before submission.

## The problem

Busy open-source projects receive more issues than maintainers can read.
New issues arrive unlabelled, with mixed quality: some are critical
security reports, some are feature ideas, some are missing the version or
the steps to reproduce. The first pass — reading, sorting, asking for
missing information — is repetitive, slow, and easy to get wrong at 2 a.m.

## The solution

TriageMinion does that first pass as one small, repeatable workflow:

1. It loads a list of GitHub issues (a JSON export, or the bundled sample).
2. Deterministic code computes verified triage facts for each issue:
   category (bug / feature / docs / security / question), priority
   (P0–P3), what information is missing, and a suggested label.
3. An OpenMinion agent reads those facts through a tool, writes a short
   Markdown triage report in its own words — top priorities first — and
   saves it through a second tool.
4. A maintainer reviews the draft. Nothing is applied to a real
   repository without a human.

The output is a report like `report.example.md` (6 sample issues) and
`report.real-issues.md` (10 real open issues from the OpenMinion
repository itself, triaged correctly: 8 bug, 2 feature).

## How it works

- `app.py` — the whole application: deterministic triage logic, two
  `@tool` functions (`get_triage_facts`, `save_report`), and the agent run.
- The agent is constructed with an explicit `session_id`, the facts tool
  is forced for the demo run (`forced_tools=["get_triage_facts"]`), and
  the runtime is managed with a context manager.
- Provider and timeout failures surface as typed errors
  (`ProviderError`, `TurnTimeoutError`) with a per-run deadline of 300 s.
- `--offline` mode runs the same workflow without a model, so anyone can
  reproduce the facts and the report shape with no key and no network.

Design choice worth noting: the model is **not** trusted to classify from
scratch. Code computes the facts first; the model's job is summarising and
prioritising — the part it is actually good at. That is what makes the
demo reproducible.

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
   real bug reports. Title-weighted scoring, a strong-phrase title
   override, and a "steps to reproduce" bonus fixed all 10 — and all 6
   samples still pass.
3. **Pinning the SDK version matters.** The public API surface is
   version-specific; `openminion==0.1.20` in `requirements.txt` is what
   the code and docs are verified against.

## Demo

A ~3-minute demo outline (live run, report walkthrough, one honest
finding) is in [SUBMISSION.md](SUBMISSION.md#demo-outline-target-3-minutes).
The video will show the real model-backed run that is already verified
locally (`report.model.md`).
