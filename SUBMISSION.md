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
