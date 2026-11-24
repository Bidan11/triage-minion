# Triage Report

Source: `real_issues_live.json` - 10 issue(s) triaged.
Decisions: 1 by the model, 9 by the fallback keyword rules (model run incomplete — repaired, see below).

**Snapshot:** 9 bug, 1 feature.

| # | Issue | Category | Priority | Missing info | Suggested labels |
|---|-------|----------|----------|--------------|------------------|
| [#821](https://github.com/openminion/openminion/issues/821) | [fetch URL policy crashes or misclassifies malformed IPv6 URLs, invalid/zero ports, and embedded whitespace or control characters](https://github.com/openminion/openminion/issues/821) | bug | P1 | reproduction steps, version / environment | `type:bug`, `priority:P1`, `area:fetch`, `security:SSRF` |
| [#819](https://github.com/openminion/openminion/issues/819) | [utility.calculate_expression raises uncaught OverflowError on float-overflowing literals/powers and skips finite/bounds checks on non-binary expressions](https://github.com/openminion/openminion/issues/819) | bug | P2 | - | `type:bug`, `priority:P2` |
| [#813](https://github.com/openminion/openminion/issues/813) | [tool: add file.mkdir and file.copy to the file family](https://github.com/openminion/openminion/issues/813) | bug | P2 | version / environment, reproduction steps | `type:bug`, `priority:P2` |
| [#811](https://github.com/openminion/openminion/issues/811) | [Agent(instructions=...) longer than ~860 characters is truncated silently; later rules never reach the model](https://github.com/openminion/openminion/issues/811) | feature | P3 | - | `type:feature`, `priority:P3` |
| [#809](https://github.com/openminion/openminion/issues/809) | [Freshness guardrail intercepts session-recall questions and refuses with a "regulation answer" message](https://github.com/openminion/openminion/issues/809) | bug | P3 | - | `type:bug`, `priority:P3` |
| [#808](https://github.com/openminion/openminion/issues/808) | [Echo (demo) provider silently produces "successful" runs that never call tools](https://github.com/openminion/openminion/issues/808) | bug | P2 | - | `type:bug`, `priority:P2` |
| [#806](https://github.com/openminion/openminion/issues/806) | [cli: capture a clipboard image into a one-shot run](https://github.com/openminion/openminion/issues/806) | bug | P2 | reproduction steps | `type:bug`, `priority:P2` |
| [#805](https://github.com/openminion/openminion/issues/805) | [memctl cannot run in the standard layout: it requires a memory.yaml file that nothing creates](https://github.com/openminion/openminion/issues/805) | bug | P2 | - | `type:bug`, `priority:P2` |
| [#804](https://github.com/openminion/openminion/issues/804) | [Agent.run with a user message over 12,000 characters returns a canned "restate the task" reply as a completed run](https://github.com/openminion/openminion/issues/804) | bug | P2 | - | `type:bug`, `priority:P2` |
| [#803](https://github.com/openminion/openminion/issues/803) | [AgentOutputValidationError reports "Invalid JSON" when the recovered JSON object fails the schema](https://github.com/openminion/openminion/issues/803) | bug | P2 | - | `type:bug`, `priority:P2` |

## Top priority

- [#821](https://github.com/openminion/openminion/issues/821) [fetch URL policy crashes or misclassifies malformed IPv6 URLs, invalid/zero ports, and embedded whitespace or control characters](https://github.com/openminion/openminion/issues/821) — P1 / bug: URL policy crashes on malformed IPv6, invalid ports, and control chars — uncaught exceptions escape fetch layer instead of returning INVALID_URL; SSRF-adjacent

## Information to request from reporters

- [#821](https://github.com/openminion/openminion/issues/821) [fetch URL policy crashes or misclassifies malformed IPv6 URLs, invalid/zero ports, and embedded whitespace or control characters](https://github.com/openminion/openminion/issues/821) — missing: reproduction steps, version / environment
- [#813](https://github.com/openminion/openminion/issues/813) [tool: add file.mkdir and file.copy to the file family](https://github.com/openminion/openminion/issues/813) — missing: version / environment, reproduction steps
- [#806](https://github.com/openminion/openminion/issues/806) [cli: capture a clipboard image into a one-shot run](https://github.com/openminion/openminion/issues/806) — missing: reproduction steps

## Repaired entries

The model run did not record decisions for: #819, #813, #811, #809, #808, #806, #805, #804, #803. Those entries above come from the fallback keyword rules and are marked as such; re-run with a model to replace them.

Next step: a maintainer reviews this draft before any label is applied.
