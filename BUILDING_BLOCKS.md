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

## Real model-backed run (2026-11-17)

Provider: **OpenRouter** (OpenMinion `openrouter` preset), key supplied via
the `OPENROUTER_API_KEY` env var. Models are swappable with
`openminion setup --provider openrouter --model <id>`.

**Samples — success.** With `cohere/north-mini-code:free` the agent called
`get_triage_facts`, wrote its own report (summary table sorted by priority,
top-priority section, missing-info notes) and called `save_report` itself.
Output: `report.model.md`. All 6 issues appear with the facts' categories
and priorities.

**Real issues — partial first attempt, then a fix.** On the 10 real
OpenMinion issues the model only received about half of the facts: the
tool result was truncated (long titles + pretty-printed JSON), and the
model honestly flagged this itself (`finalization_status: incomplete`,
"only 5 complete issues were retrieved"). One truncated title also led it
to mislabel issue 767. That run is kept as `report.real-model.partial.md`.
Fix applied in `get_triage_facts`: compact JSON (no pretty-printing) and
titles capped at 120 characters, plus an instruction to copy category and
priority from the facts exactly.

**Clean re-run — success (2026-11-17).** Compacting alone was not enough:
the payload was only ~2.3 KB, yet the model still received it cut off
after ~6 issues. The facts tool now **paginates** (4 issues per call, the
model passes `offset` 0, 4, 8 and sees the total). With that, a full run
via `openrouter/free` covered **all 10 issues** and the model called
`save_report` itself: `report.real-model.md` — 8 bug / 2 feature, exactly
matching the deterministic facts, #752 (bare-command crash) correctly
surfaced as the P1 top item, missing-info notes for #752, #754, #757.
Two honest caveats from the same session: the Cohere free endpoint
returned `EMPTY_PROVIDER_RESPONSE` twice in a row after working earlier
(free endpoints are flaky — the `openrouter/free` router routed around
it), and one intermediate run printed its report as plain text instead
of calling `save_report`, which is why the instructions now state the
save step as a hard requirement.

### Findings from getting the run to work

1. **Proxied environments can break the SDK's HTTP client.** In our
   sandbox, `NO_PROXY` contains bracketed IPv6 entries (`[::1]`, …).
   `httpx` fails on them with `InvalidURL: Invalid port: ':1]'`, so every
   provider call died before it started — while `curl` worked fine.
   Sanitising `NO_PROXY=localhost,127.0.0.1` for SDK runs fixed it.
2. **Custom tools block headless runs until policy allows them.** Our
   `@tool` functions are classified risk `write` / reversibility
   `unknown`, so the runtime demanded an interactive policy confirmation
   and a non-interactive run stalled at the prompt. Setting
   `action_policy.default_action: "allow"` alone did **not** lift it;
   per-tool rules in `.openminion/agents.json` did:
   `{"match": {"tool_name": "get_triage_facts"}, "mode": "auto"}` (same
   for `save_report`). Worth knowing for any CI/demo automation.
3. **Free models vary wildly for agent turns.** `nvidia/nemotron-3-ultra`
   (free) was still thinking after 120 s (we raised the per-run deadline
   to 300 s); `google/gemma-4-31b-it` (free) hit a provider rate limit
   immediately; `cohere/north-mini-code:free` completed the full
   two-tool workflow in ~45 s. OpenRouter's free tier allows 50 model
   requests/day per account — plan demo recordings around that.
4. **Typed errors helped.** The rate limit surfaced as a `ProviderError`
   with a clear `RATE_LIMITED` reason, and the slow model as a
   `TurnTimeoutError` — both handled in `app.py` without a crash.

## Still to test

- The demo recording (screen capture of the verified run + voiceover).
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
4. Tool results have a practical size budget: on larger inputs, keep the
   facts payload compact or the model silently sees a truncated set (to
   its credit, the model noticed and said so).
5. "It works in the CLI" is not "it works headless": policy confirmations
   and proxy env vars only show up when you run the SDK unattended.
