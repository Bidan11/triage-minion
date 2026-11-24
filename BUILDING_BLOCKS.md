# Building Blocks Tested — TriageMinion

For Cortensor Hackathon #5. Honest notes: verified facts only, updated as
testing continues. Format: a summary table first, then each finding
written as a reproducible mini bug report (steps, expected vs actual,
workaround we shipped).

## Summary — blocks used, and how each behaved

| Building block | How we used it | Worked / Didn't work |
|---|---|---|
| Python SDK install | `pip install openminion==0.1.20` in a fresh venv (Python 3.12); documented import check (`Agent, ProviderError, TurnTimeoutError, tool`, `openminion.api` types) | **Worked.** Imports pass as documented. Pinning the version matters — the API surface is version-specific. |
| Decorated tools (`@tool`) | `get_issue_page`, `record_triage`, `save_report` passed via `tools=[...]`, exposed only for the run | **Worked**, with two rough edges: tool results can arrive truncated (Finding 1) and custom tools block headless runs until policy allows them (Finding 2). |
| Structured decision tool | `record_triage`: the model records category / priority / labels / missing info / reason as enum-validated data; the report renders from the records | **Worked.** This is what makes a model run auditable, validatable and repairable — the core of the current design. |
| Tool-result paging | `get_issue_page` returns 4 issues per call; the model pages with `offset` 0, 4, 8 | **Worked** — shipped as the workaround for Finding 1 (truncation). |
| Action policy / permissions | Per-tool rules `{"match": {"tool_name": "..."}, "mode": "auto"}` in `.openminion/agents.json` | **Didn't work as first configured** — `action_policy.default_action: "allow"` alone did not lift the interactive confirmation; per-tool rules did (Finding 2). Rules are name-based, so a tool rename silently re-blocks runs (also Finding 2). |
| Sessions | Explicit `session_id="triage-minion-demo"` | **Worked.** Run completes inside the named session; session id returned on the result. |
| Runtime lifecycle | `with Agent(...) as agent:` context manager | **Worked.** Runtime closes cleanly, no hanging process. |
| Forced tools | `forced_tools=["get_issue_page"]` so the demo always exercises the issue-page tool | **Worked.** (Under the previous design, forcing *both* tools caused `EMPTY_PROVIDER_RESPONSE`; forcing the read tool only was stable.) |
| Provider — OpenRouter preset | `openrouter` preset, key via `OPENROUTER_API_KEY` env var; free models (`openrouter/free`, `cohere/north-mini-code:free`) | **Worked, inconsistently** — free endpoints are flaky: empty responses, rate limits, and runs that stop early (Finding 3). |
| Provider — echo | `openminion config init --provider echo`, full app run | **Worked as a wiring check only.** Echo repeats the prompt; it cannot prove model-selected tool use, exactly as the docs warn. A tool-capable provider is required for any real demo. |
| Typed error handling | `ProviderError` / `TurnTimeoutError` handled in `app.py`; per-run deadline `timeout_seconds=300` | **Worked.** Rate limits surfaced as `ProviderError` with a clear `RATE_LIMITED` reason; a slow model as `TurnTimeoutError` — no crashes. |
| Report validation + repair | After any run, recorded decisions are validated against the input; `save_report` refuses to save while decisions are missing; gaps are fallback-filled and disclosed | **Worked** — shipped after Finding 4 (partial runs were previously saved silently). |
| Diagnostics from the model itself | The model flagged its own incomplete input in the truncated run (`finalization_status: incomplete`, "only 5 complete issues were retrieved") | **Worked** — the agent noticed the truncation before we did; that honesty is what made Finding 1 diagnosable. |
| Live GitHub fetch (our code, SDK-adjacent) | `app.py --github OpenMinion/openminion --limit 10` against the public REST API | **Worked**, with an API gotcha: the issues endpoint interleaves pull requests (Finding 6). |
| Own-repo actions (our code) | `github_actions.py`: dry-run plan by default; `--apply` posts labels + a triage comment; refuses repos the token does not own | **Worked live (2026-11-23)** on our own repo — issues #1 and #2 of Bidan11/triage-minion carry real TriageMinion labels and comments. |

## Findings — mini bug reports

### Finding 1: Tool results arrive truncated on medium-sized payloads

- **Steps to reproduce:** Give the agent a tool that returns the facts
  for 10 GitHub issues at once (title + category + priority + missing
  info per issue). First attempt: pretty-printed JSON with full titles.
  Second attempt: compact JSON, total payload ≈ 2.3 KB.
- **Expected:** The model receives the complete tool result both times —
  2.3 KB is a small payload.
- **Actual:** Both times the model received the result cut off after
  ~6 of the 10 issues. With the pretty-printed payload it flagged the
  run `incomplete` itself and reported only 5 complete issues; one
  truncated title also led it to mislabel issue #767. The truncated
  first attempt is kept at `archive/report.real-model.partial.md`.
- **Workaround we shipped:** Paginate the tool — `get_issue_page`
  returns 4 issues per call and the model pages through with `offset`.
  With paging, a full run covered all 10 issues. (This finding is our
  bonus-track bug candidate — see SUBMISSION.md.)

### Finding 2: Custom tools block headless runs; policy is name-based

- **Steps to reproduce:** Register custom `@tool` functions (classified
  risk `write` / reversibility `unknown`) and run the agent
  non-interactively (stdin closed, e.g. in CI or a screen recording).
  Then, separately: set `action_policy.default_action: "allow"` in
  `.openminion/agents.json` and run again. Finally, rename a tool and
  run once more without touching the config.
- **Expected:** A documented global allow setting lets the run proceed
  unattended; renaming a tool does not silently change policy behaviour.
- **Actual:** The run stalls at an interactive policy confirmation.
  `default_action: "allow"` alone did **not** lift it; only per-tool
  rules — `{"match": {"tool_name": "get_issue_page"}, "mode": "auto"}`
  (and likewise for `record_triage`, `save_report`) — let the run
  proceed. And because the rules match by tool *name*, when our tools
  were renamed during the 2026-11-21 redesign, the stale rule for the
  old tool name was silently useless and the new tools had no rules
  until we added them — the same headless block would have returned.
- **Workaround we shipped:** Per-tool `mode: "auto"` rules for all
  three current tool names, documented in the README setup section;
  the rule names are now part of our pre-run checklist.

### Finding 3: Free models are inconsistent agent drivers

- **Steps to reproduce:** Run the same agent workflow on OpenRouter
  free models: `nvidia/nemotron-3-ultra-550b-a55b:free`,
  `google/gemma-4-31b-it:free`, `cohere/north-mini-code:free`,
  `openrouter/free`.
- **Expected:** Roughly comparable completion of a simple
  read → record → save workflow.
- **Actual:** Nemotron was still thinking after 120 s (we raised the
  per-run deadline to 300 s); Gemma hit a provider rate limit
  immediately; Cohere completed the full workflow in ~45 s but also
  returned `EMPTY_PROVIDER_RESPONSE` twice in a row in a later session;
  on 2026-11-23 the same workflow produced one run where the model
  recorded 7/10 decisions (`report.live-model.md`) and a later run
  where it recorded only 1/10 before stopping
  (`report.live-model-v3.md`). OpenRouter's free tier allows 50 model
  requests/day per account, which also caps retakes.
- **Workaround we shipped:** Design for unreliable models instead of
  trusting them — structured `record_triage` decisions, validation of
  coverage after every run, disclosed fallback repair (Finding 4), and
  the `openrouter/free` router as the default so routing can move
  between endpoints.

### Finding 4: A partial model run used to save a partial report, silently

- **Steps to reproduce:** (Previous design.) Let a model run end after
  it has recorded decisions for only some of the input issues, then
  call the save step.
- **Expected:** The save step refuses, or the report clearly marks the
  missing coverage.
- **Actual:** The old behaviour kept a model-saved report even if it
  covered 6 of 10 issues, with no marker that 4 were missing. A
  "successful" run could ship an incomplete triage.
- **Workaround we shipped:** Every run now ends with validation
  against the input: duplicates collapse, missing decisions are filled
  by the fallback rules and disclosed in a "Repaired entries" section,
  and `save_report` refuses to save while decisions are missing,
  telling the model which issue ids remain. Pinned by tests.

### Finding 5: Bracketed IPv6 in `NO_PROXY` breaks the SDK's HTTP client *(environment quirk, not an SDK bug)*

- **Steps to reproduce:** In a proxied sandbox whose `no_proxy`
  contains bracketed IPv6 entries (`[::1]`, …), make any provider call
  through the SDK.
- **Expected:** The provider call goes through, as it does with `curl`
  in the same environment.
- **Actual:** `httpx` fails with `InvalidURL: Invalid port: ':1]'` and
  every provider call dies before it starts.
- **Workaround we shipped:** Run SDK commands with
  `NO_PROXY=localhost,127.0.0.1`. We label this an environment quirk —
  the malformed value is ours, not the SDK's — and document it so other
  sandbox/CI users recognise the symptom.

### Finding 6: The GitHub issues endpoint interleaves pull requests

- **Steps to reproduce:** Fetch the newest 30 items from
  `GET /repos/OpenMinion/openminion/issues` and count them as issues.
- **Expected:** 30 issues.
- **Actual:** 12 of the newest 30 items were pull requests. Any client
  that counts before filtering silently under-fetches.
- **Workaround we shipped:** Our fetch client filters out PR items
  first and keeps paging until it has `limit` real issues; parsing is
  pinned by a test against a recorded real API payload that includes a
  PR item.

## Design decision worth reporting (2026-11-16 — SUPERSEDED 2026-11-21)

The model is **not** trusted to classify issues from scratch. Deterministic
code computes category/priority facts first, and the agent must read them
through the facts tool (`forced_tools=["get_triage_facts"]`). This made the
demo reproducible: the same input always produces the same facts, and the
model's job is limited to summarising and prioritising — the part it is
actually good at.

> **Update (2026-11-21):** a code review pushed back on exactly this —
> if code classifies and the model only writes prose, the "meaningful
> SDK usage" is thin and the agent is not really an agent. The design
> was inverted: the model now classifies and records structured
> decisions; the keyword rules survive only as an offline fallback and
> repair filler. See "Redesign after code review" below.

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
exists so the demo is reproducible offline and so incomplete model runs
can be repaired with disclosed, deterministic decisions. In the online
run the model classifies; a maintainer reviews the draft before
anything is applied.

## Redesign after code review (2026-11-21)

An external review of the repo raised ten findings; the code fixes
landed the same night. What changed, and what we learned doing it:

1. **Model-led classification (was: facts-first).** The agent now reads
   raw issues through the paged `get_issue_page` tool and records each
   decision through a new structured tool, `record_triage` (category,
   priority, labels, missing info, one-line reason). The report is
   rendered from those records — structured tool output, not free-text
   prose, is what makes a model run auditable. The "never re-classify"
   instruction is gone.
2. **A real GitHub connection.** `app.py --github OpenMinion/openminion
   --limit 10` fetches open issues live from the REST API
   (unauthenticated; verified from the sandbox — `real_issues_live.json`).
   Two API lessons: the issues endpoint **interleaves pull requests**
   (12 of the newest 30 items were PRs), so filtering must happen
   before counting the limit; and the unauthenticated rate limit
   (60/hour) is ample for demos but argues for the optional token.
   A separate `github_actions.py` applies labels and posts triage
   comments on the **owner's own** repo: dry-run by default, `--apply`
   to write, and it refuses repos the token does not own.
   **Update (2026-11-23):** the live `--apply` demo has now been run —
   issues #1 and #2 of Bidan11/triage-minion received real labels and
   triage comments.
3. **Partial runs are repaired, not shipped.** The old behaviour kept a
   model-saved report even if it covered 6 of 10 issues. Now every run
   ends with validation against the input; gaps are filled by the
   fallback rules and disclosed in a "Repaired entries" section
   (Finding 4).
4. **One report format.** A single renderer serves offline, online and
   repair paths; reports now carry full untruncated titles and
   clickable issue links.
5. **The fallback rules were fragile in exactly the ways a reviewer
   would poke:** a bare "add " forced `feature`, a bare "?" forced
   `question`, a bare "500" forced P1, and the word "security" forced
   the security category even for a feature request *about* security.
   All four are fixed and pinned by regression tests; "environment
   provided" is now judged from the issue **body** only (a "[0.1.22]"
   title tag is not the reporter's environment).
6. **Tests exist now.** 35 pytest tests run fully offline (classifier
   expectations on all 16 known issues, renderer, repair, fetch
   parsing from a recorded fixture). "Offline mode" is no longer the
   only verification story.

**Live verification of the redesign (2026-11-23).** The model-led flow
has now had real model runs via OpenRouter: `report.live-model.md`
(model recorded 7/10 decisions itself on the live-fetched issues;
3 repaired and disclosed) and a second run the same day,
`report.live-model-v3.md` (model recorded 1/10 before stopping;
9 repaired and disclosed). The gap between the two runs is Finding 3
in action — and exactly why the validation/repair layer exists. A
final run on 2026-11-24 (`report.live-model-v4.md`) recorded 10/10
decisions itself with no repairs; that is the run filmed for the
current demo video.

## Still to test

- Behaviour on a large issue list (100+ issues): turn timeouts, context
  limits, and whether chunking per session is needed.
- Approval flow for a "dangerous" tool variant of `save_report`.

## What we learned

1. Pinning `openminion==0.1.20` in `requirements.txt` matters — the public
   API surface is version-specific and the quickstart is written against it.
2. The echo provider is a good wiring check but a misleading demo: it looks
   like a run happened while no tool was ever called. Our app therefore
   labels its fallback output instead of pretending the model produced it.
3. Structured decision tools beat free-text reports: when the model must
   record each classification through a tool, the result is auditable,
   validatable, and repairable. (This replaced our earlier facts-first
   design, where code classified and the model only wrote prose — more
   reproducible, but barely an agent.)
4. Tool results have a practical size budget: on larger inputs, keep the
   facts payload compact or the model silently sees a truncated set (to
   its credit, the model noticed and said so).
5. "It works in the CLI" is not "it works headless": policy confirmations
   and proxy env vars only show up when you run the SDK unattended.
