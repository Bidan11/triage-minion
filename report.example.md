# Triage Report

Source: `sample_issues.json` - 6 issue(s) triaged.
Decisions: fallback keyword rules (no model run).

**Snapshot:** 2 bug, 1 feature, 1 docs, 1 security, 1 question.

| # | Issue | Category | Priority | Missing info | Suggested labels |
|---|-------|----------|----------|--------------|------------------|
| #101 | App crash on login after 2.4.0 update | bug | P0 | reproduction steps | `type:bug`, `priority:P0` |
| #102 | Add support for dark mode | feature | P3 | - | `type:feature`, `priority:P3` |
| #103 | Typo in README installation section | docs | P3 | - | `type:docs`, `priority:P3` |
| #104 | API token exposed in example config? | security | P0 | version / environment, reproduction steps | `type:security`, `priority:P0` |
| #105 | Export sometimes fails with 500 | bug | P1 | version / environment, reproduction steps | `type:bug`, `priority:P1` |
| #106 | How to run the project locally? | question | P3 | - | `type:question`, `priority:P3` |

## Top priority

- #101 App crash on login after 2.4.0 update — P0 / bug: Keyword fallback: 'error' in body; 'crash' in title; 'crash' in body
- #104 API token exposed in example config? — P0 / security: Keyword fallback: 'security' in body; 'token exposed' in title; strong signal 'token exposed'
- #105 Export sometimes fails with 500 — P1 / bug: Keyword fallback: 'error' in body; 'fails' in title; 'fails' in body

## Information to request from reporters

- #101 App crash on login after 2.4.0 update — missing: reproduction steps
- #104 API token exposed in example config? — missing: version / environment, reproduction steps
- #105 Export sometimes fails with 500 — missing: version / environment, reproduction steps

Next step: a maintainer reviews this draft before any label is applied.
