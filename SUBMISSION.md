# Submission — Cortensor Hackathon #5 (DoraHacks)

- Event: https://dorahacks.io/hackathon/2418/detail
- Submission deadline: **December 18, 2026 (Pacific Time)**
- Prize pool: $1,150 in $COR (1st $500 / 2nd $300 / 3rd $200 / 4th $100 / 5th $50;
  50% liquid, 50% in a one-month staking lock)
- How to submit: PR to the dedicated Hackathon #5 repository (URL announced
  by the organisers) linking the public project + materials, plus the
  DoraHacks BUIDL page.

## Checklist (from the official page)

- [ ] Public source repository with README (setup + run instructions)
- [ ] Short explanation of the OpenMinion SDK workflow — in README
- [ ] One working example — `sample_issues.json` + `report.example.md`
- [ ] 1–5 minute demo video showing a **real model-backed run**
- [ ] "Building Blocks Tested" note — BUILDING_BLOCKS.md
- [ ] "What We Learned" note with actionable feedback — BUILDING_BLOCKS.md
- [ ] Participant can explain and demonstrate the project (rules requirement)

## Evaluation weights (official)

- Working functionality and useful outcome — 25%
- Meaningful OpenMinion SDK usage — 20%
- Reproducibility and demo quality — 20%
- Building-block findings and improvement feedback — 25%
- Relevance to Cortensor builder workflows — 10%

## Demo outline (target ~3 minutes)

1. (0:00) The problem: a maintainer facing a pile of untriaged issues.
2. (0:30) Show `sample_issues.json` — 6 real-looking issues.
3. (0:45) Run `python app.py --github OpenMinion/openminion` live; show
   the agent fetching issues, classifying each one itself via
   `record_triage`, then saving the report rendered from its decisions.
4. (1:45) Open `report.md`: security issue flagged P0, login crash P0/P1,
   docs typo P3 — and the "missing info" column.
5. (2:30) One honest finding from BUILDING_BLOCKS.md (echo provider cannot
   prove tool use; why decisions are recorded as structured tool calls).
6. (2:50) Close: what a maintainer does next with the draft report.

## Bonus track: bug report + fix PR

> **DRAFT — not filed.** Per the bonus rules, a bug report alone does
> not qualify: the report must be acknowledged by the Cortensor /
> OpenMinion team and confirmed in scope *before* a fix PR counts.
> Filing needs the owner's GitHub token. Nothing below has been
> submitted anywhere yet.

**Chosen candidate: tool-result truncation (Finding 1 in
BUILDING_BLOCKS.md).** Why this one, over the headless-policy finding:
the policy behaviour (per-tool `mode: "auto"` rules) is plausibly
*intended* safety design with a configuration path, so calling it a bug
is hard to defend. The truncation is different — it is silent data
loss inside the agent loop: a tool result of only ≈ 2.3 KB reached the
model cut off after ~6 of 10 items, twice, and the only reason we know
is that the model happened to notice and say so. Any agent whose tools
return moderately sized results can lose data the same way without
noticing.

### (a) Draft GitHub issue text

**Title:** Tool result truncated before reaching the model (≈2.3 KB payload cut after ~60% of items, no truncation signal)

**Body:**

> **Versions:** observed on OpenMinion SDK **0.1.20** (pinned in our
> `requirements.txt`). Upstream has since released **0.1.22**; we have
> not yet re-verified against 0.1.22 because the project is pinned to
> 0.1.20 — happy to re-test on the version you prefer.
>
> **Environment:** Python 3.12, provider OpenRouter (free models,
> incl. `cohere/north-mini-code:free` and `openrouter/free`),
> non-interactive run.
>
> **Steps to reproduce:**
> 1. Register a `@tool` that returns structured facts for 10 items at
>    once (per item: title, category, priority, missing-info list).
> 2. Run an agent turn that calls the tool once and asks the model to
>    work with all 10 items.
> 3. Observe what the model reports receiving. We reproduced this with
>    two payload shapes: (a) pretty-printed JSON with full titles, and
>    (b) compact JSON, total ≈ 2.3 KB.
>
> **Expected:** The model receives the complete tool result in both
> cases — 2.3 KB is a small payload — or, if a size budget is
> enforced, the result carries an explicit truncation marker (original
> length / items omitted) that the model or the application can
> detect and react to.
>
> **Actual:** In both shapes the model received the result cut off
> after ~6 of the 10 items, with no truncation indication in what it
> received. In attempt (a) the model flagged its own run
> `incomplete` ("only 5 complete issues were retrieved") and one
> truncated title led it to mislabel an issue; that run's output is
> preserved in our repo as `archive/report.real-model.partial.md`.
> In attempt (b) the compact ≈ 2.3 KB payload was still cut at the
> same place.
>
> **Workaround we shipped:** Paginate the tool (4 items per call, the
> model pages with an offset parameter). With paging, full runs cover
> all 10 items reliably. This works, but every agent author has to
> discover the budget by losing data first.
>
> **Suggested directions:** surface truncation explicitly (marker +
> original size in the tool result the model sees), document the
> effective budget, or make the budget configurable per tool — any of
> these turns a silent failure into a designable behaviour.

### (b) Draft fix-PR plan (only after team acknowledgement)

1. **Reproduce minimally:** a synthetic tool returning payloads of
   increasing, exactly-known sizes; assert what the model-facing tool
   result contains at each size, on the SDK version the team points
   us at (0.1.20 first, then current).
2. **Locate the cut:** trace the tool result through the agent loop —
   tool execution → tool-result storage → provider message assembly —
   and identify which layer truncates and whether any configured
   limit governs it.
3. **Fix narrowly:** at the truncation point, append an explicit
   truncation marker (original length, amount omitted) instead of
   cutting silently; if a configuration knob exists but is not
   honoured, honour it. No behaviour change for results under the
   budget.
4. **Regression tests:** boundary tests just below / at / above the
   budget asserting (i) complete delivery below it and (ii) a visible
   marker above it.
5. **Verify:** re-run the reproduction and our project's original
   10-issue single-call scenario; the model must either receive all
   10 items or receive a marker it can act on.
