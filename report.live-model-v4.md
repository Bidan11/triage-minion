# Triage Report

Source: `real_issues_live.json` - 10 issue(s) triaged.
Decisions: recorded by the model via the record_triage tool.

**Snapshot:** 7 bug, 2 feature, 1 security.

| # | Issue | Category | Priority | Missing info | Suggested labels |
|---|-------|----------|----------|--------------|------------------|
| [#821](https://github.com/openminion/openminion/issues/821) | [fetch URL policy crashes or misclassifies malformed IPv6 URLs, invalid/zero ports, and embedded whitespace or control characters](https://github.com/openminion/openminion/issues/821) | security | P1 | - | `type:security`, `priority:P1`, `area:tools`, `area:fetch` |
| [#819](https://github.com/openminion/openminion/issues/819) | [utility.calculate_expression raises uncaught OverflowError on float-overflowing literals/powers and skips finite/bounds checks on non-binary expressions](https://github.com/openminion/openminion/issues/819) | bug | P1 | - | `type:bug`, `priority:P1`, `area:tools`, `area:utility` |
| [#813](https://github.com/openminion/openminion/issues/813) | [tool: add file.mkdir and file.copy to the file family](https://github.com/openminion/openminion/issues/813) | feature | P2 | - | `type:enhancement`, `priority:P2`, `area:tools` |
| [#811](https://github.com/openminion/openminion/issues/811) | [Agent(instructions=...) longer than ~860 characters is truncated silently; later rules never reach the model](https://github.com/openminion/openminion/issues/811) | bug | P2 | - | `type:bug`, `priority:P2`, `area:sdk`, `area:brain` |
| [#809](https://github.com/openminion/openminion/issues/809) | [Freshness guardrail intercepts session-recall questions and refuses with a "regulation answer" message](https://github.com/openminion/openminion/issues/809) | bug | P1 | - | `type:bug`, `priority:P1`, `area:brain`, `area:guardrails` |
| [#808](https://github.com/openminion/openminion/issues/808) | [Echo (demo) provider silently produces "successful" runs that never call tools](https://github.com/openminion/openminion/issues/808) | bug | P2 | - | `type:bug`, `priority:P2`, `area:sdk`, `area:providers` |
| [#806](https://github.com/openminion/openminion/issues/806) | [cli: capture a clipboard image into a one-shot run](https://github.com/openminion/openminion/issues/806) | feature | P3 | - | `type:enhancement`, `priority:P3`, `area:tools`, `area:artifacts`, `area:cli` |
| [#805](https://github.com/openminion/openminion/issues/805) | [memctl cannot run in the standard layout: it requires a memory.yaml file that nothing creates](https://github.com/openminion/openminion/issues/805) | bug | P1 | - | `type:bug`, `priority:P1`, `area:config`, `area:cli` |
| [#804](https://github.com/openminion/openminion/issues/804) | [Agent.run with a user message over 12,000 characters returns a canned "restate the task" reply as a completed run](https://github.com/openminion/openminion/issues/804) | bug | P1 | - | `type:bug`, `priority:P1`, `area:sdk`, `area:brain` |
| [#803](https://github.com/openminion/openminion/issues/803) | [AgentOutputValidationError reports "Invalid JSON" when the recovered JSON object fails the schema](https://github.com/openminion/openminion/issues/803) | bug | P2 | - | `type:bug`, `priority:P2`, `area:sdk` |

## Top priority

- [#821](https://github.com/openminion/openminion/issues/821) [fetch URL policy crashes or misclassifies malformed IPv6 URLs, invalid/zero ports, and embedded whitespace or control characters](https://github.com/openminion/openminion/issues/821) — P1 / security: Security boundary issue in fetch URL policy: malformed IPv6 URLs, invalid ports, and control chars can crash or bypass SSRF protections. Clear repro paths given.
- [#819](https://github.com/openminion/openminion/issues/819) [utility.calculate_expression raises uncaught OverflowError on float-overflowing literals/powers and skips finite/bounds checks on non-binary expressions](https://github.com/openminion/openminion/issues/819) — P1 / bug: Uncaught OverflowError in utility.calculate_expression and bypass of finite/bounds checks on non-binary expressions. Detailed repro and root cause provided.
- [#809](https://github.com/openminion/openminion/issues/809) [Freshness guardrail intercepts session-recall questions and refuses with a "regulation answer" message](https://github.com/openminion/openminion/issues/809) — P1 / bug: Freshness guardrail falsely refuses session-recall questions, blocking basic multi-turn agent behavior. Version and repro steps given.
- [#805](https://github.com/openminion/openminion/issues/805) [memctl cannot run in the standard layout: it requires a memory.yaml file that nothing creates](https://github.com/openminion/openminion/issues/805) — P1 / bug: memctl unusable in standard layout: requires memory.yaml that nothing creates, aborts with FileNotFoundError. Version and repro steps given.
- [#804](https://github.com/openminion/openminion/issues/804) [Agent.run with a user message over 12,000 characters returns a canned "restate the task" reply as a completed run](https://github.com/openminion/openminion/issues/804) — P1 / bug: Agent.run silently returns canned reply for messages over 12k chars, marked completed with no error. Environment and repro provided.

Next step: a maintainer reviews this draft before any label is applied.
