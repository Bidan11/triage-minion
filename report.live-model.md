# Triage Report

Source: `real_issues_live.json` - 10 issue(s) triaged.
Decisions: 7 by the model, 3 by the fallback keyword rules (model run incomplete — repaired, see below).

**Snapshot:** 7 bug, 3 feature.

| # | Issue | Category | Priority | Missing info | Suggested labels |
|---|-------|----------|----------|--------------|------------------|
| [#821](https://github.com/openminion/openminion/issues/821) | [fetch URL policy crashes or misclassifies malformed IPv6 URLs, invalid/zero ports, and embedded whitespace or control characters](https://github.com/openminion/openminion/issues/821) | bug | P1 | - | `type:bug`, `priority:P1`, `security`, `fetch` |
| [#819](https://github.com/openminion/openminion/issues/819) | [utility.calculate_expression raises uncaught OverflowError on float-overflowing literals/powers and skips finite/bounds checks on non-binary expressions](https://github.com/openminion/openminion/issues/819) | bug | P1 | - | `type:bug`, `priority:P1`, `utility` |
| [#813](https://github.com/openminion/openminion/issues/813) | [tool: add file.mkdir and file.copy to the file family](https://github.com/openminion/openminion/issues/813) | feature | P2 | - | `type:feature`, `enhancement`, `file-tools` |
| [#811](https://github.com/openminion/openminion/issues/811) | [Agent(instructions=...) longer than ~860 characters is truncated silently; later rules never reach the model](https://github.com/openminion/openminion/issues/811) | feature | P3 | - | `type:feature`, `priority:P3` |
| [#809](https://github.com/openminion/openminion/issues/809) | [Freshness guardrail intercepts session-recall questions and refuses with a "regulation answer" message](https://github.com/openminion/openminion/issues/809) | bug | P1 | - | `type:bug`, `priority:P1`, `area:brain`, `freshness` |
| [#808](https://github.com/openminion/openminion/issues/808) | [Echo (demo) provider silently produces "successful" runs that never call tools](https://github.com/openminion/openminion/issues/808) | bug | P2 | - | `type:bug`, `priority:P2`, `area:sdk`, `area:providers` |
| [#806](https://github.com/openminion/openminion/issues/806) | [cli: capture a clipboard image into a one-shot run](https://github.com/openminion/openminion/issues/806) | feature | P3 | - | `type:feature`, `enhancement`, `cli`, `clipboard`, `images` |
| [#805](https://github.com/openminion/openminion/issues/805) | [memctl cannot run in the standard layout: it requires a memory.yaml file that nothing creates](https://github.com/openminion/openminion/issues/805) | bug | P2 | - | `type:bug`, `priority:P2` |
| [#804](https://github.com/openminion/openminion/issues/804) | [Agent.run with a user message over 12,000 characters returns a canned "restate the task" reply as a completed run](https://github.com/openminion/openminion/issues/804) | bug | P1 | - | `type:bug`, `priority:P1`, `brain`, `agent-run` |
| [#803](https://github.com/openminion/openminion/issues/803) | [AgentOutputValidationError reports "Invalid JSON" when the recovered JSON object fails the schema](https://github.com/openminion/openminion/issues/803) | bug | P2 | - | `type:bug`, `priority:P2` |

## Top priority

- [#821](https://github.com/openminion/openminion/issues/821) [fetch URL policy crashes or misclassifies malformed IPv6 URLs, invalid/zero ports, and embedded whitespace or control characters](https://github.com/openminion/openminion/issues/821) — P1 / bug: Detailed bug report about URL parsing vulnerabilities (malformed IPv6, invalid ports, whitespace/control chars) causing crashes and potential SSRF bypass in fetch policy
- [#819](https://github.com/openminion/openminion/issues/819) [utility.calculate_expression raises uncaught OverflowError on float-overflowing literals/powers and skips finite/bounds checks on non-binary expressions](https://github.com/openminion/openminion/issues/819) — P1 / bug: Utility calculate_expression has uncaught OverflowError on float-overflowing literals/powers and skips finite/bounds checks on non-binary expressions
- [#809](https://github.com/openminion/openminion/issues/809) [Freshness guardrail intercepts session-recall questions and refuses with a "regulation answer" message](https://github.com/openminion/openminion/issues/809) — P1 / bug: Freshness guardrail misfires on session-recall questions, refusing a basic multi-turn pattern with an irrelevant message
- [#804](https://github.com/openminion/openminion/issues/804) [Agent.run with a user message over 12,000 characters returns a canned "restate the task" reply as a completed run](https://github.com/openminion/openminion/issues/804) — P1 / bug: Agent.run with >12k chars returns canned "restate task" reply instead of raising error

## Repaired entries

The model run did not record decisions for: #811, #805, #803. Those entries above come from the fallback keyword rules and are marked as such; re-run with a model to replace them.

Next step: a maintainer reviews this draft before any label is applied.
