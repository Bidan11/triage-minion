# Triage Report

Source: `real_issues.json` - 10 issue(s) triaged.
Decisions: fallback keyword rules (no model run).

**Snapshot:** 8 bug, 2 feature.

| # | Issue | Category | Priority | Missing info | Suggested labels |
|---|-------|----------|----------|--------------|------------------|
| [#774](https://github.com/OpenMinion/openminion/issues/774) | [[0.1.22] Handoff cannot bound or approve the delegated target run: build_delegate_tool calls target.run(message) with no timeout or approval_callback](https://github.com/OpenMinion/openminion/issues/774) | bug | P2 | - | `type:bug`, `priority:P2` |
| [#773](https://github.com/OpenMinion/openminion/issues/773) | [[0.1.22] TurnResponse.telemetry reports 0 tokens when usage_*_tokens metadata keys are absent (no in-tree producer)](https://github.com/OpenMinion/openminion/issues/773) | bug | P3 | - | `type:bug`, `priority:P3` |
| [#770](https://github.com/OpenMinion/openminion/issues/770) | [[0.1.22] Agent.run(timeout_seconds=...) cannot extend the 300 s brain turn budget, and the budget stop is returned as a normal reply](https://github.com/OpenMinion/openminion/issues/770) | bug | P2 | - | `type:bug`, `priority:P2` |
| [#769](https://github.com/OpenMinion/openminion/issues/769) | [[0.1.22] Runtime bootstrap fails on Windows (WinError 206) because browser-playwright artifact dirs are created under the CWD even when no browser tool is used](https://github.com/OpenMinion/openminion/issues/769) | bug | P2 | - | `type:bug`, `priority:P2` |
| [#767](https://github.com/OpenMinion/openminion/issues/767) | [cli: add `config diff` so an import can be previewed before it overwrites the config](https://github.com/OpenMinion/openminion/issues/767) | feature | P3 | - | `type:feature`, `priority:P3` |
| [#766](https://github.com/OpenMinion/openminion/issues/766) | [storage: empty storage.path ("") in agents.json resolves to data_root directory and fails with sqlite3.OperationalError](https://github.com/OpenMinion/openminion/issues/766) | bug | P2 | - | `type:bug`, `priority:P2` |
| [#759](https://github.com/OpenMinion/openminion/issues/759) | [llm: add a provider cooldown registry and honour Retry-After instead of a constant retry backoff](https://github.com/OpenMinion/openminion/issues/759) | feature | P2 | - | `type:feature`, `priority:P2` |
| [#757](https://github.com/OpenMinion/openminion/issues/757) | [turn-input: an accepted `steer_current` is never applied or retired when its turn ends, and 20 of them wedge the session queue (QUEUE_FULL)](https://github.com/OpenMinion/openminion/issues/757) | bug | P3 | version / environment, reproduction steps | `type:bug`, `priority:P3` |
| [#754](https://github.com/OpenMinion/openminion/issues/754) | [cli: `mcp import --from` reports a missing or malformed source file as an internal error](https://github.com/OpenMinion/openminion/issues/754) | bug | P2 | version / environment, reproduction steps | `type:bug`, `priority:P2` |
| [#752](https://github.com/OpenMinion/openminion/issues/752) | [cli: bare `openminion replay` crashes with AttributeError instead of usage](https://github.com/OpenMinion/openminion/issues/752) | bug | P1 | version / environment, reproduction steps | `type:bug`, `priority:P1` |

## Top priority

- [#752](https://github.com/OpenMinion/openminion/issues/752) [cli: bare `openminion replay` crashes with AttributeError instead of usage](https://github.com/OpenMinion/openminion/issues/752) — P1 / bug: Keyword fallback: 'error' in title; 'error' in body; 'crash' in title

## Information to request from reporters

- [#757](https://github.com/OpenMinion/openminion/issues/757) [turn-input: an accepted `steer_current` is never applied or retired when its turn ends, and 20 of them wedge the session queue (QUEUE_FULL)](https://github.com/OpenMinion/openminion/issues/757) — missing: version / environment, reproduction steps
- [#754](https://github.com/OpenMinion/openminion/issues/754) [cli: `mcp import --from` reports a missing or malformed source file as an internal error](https://github.com/OpenMinion/openminion/issues/754) — missing: version / environment, reproduction steps
- [#752](https://github.com/OpenMinion/openminion/issues/752) [cli: bare `openminion replay` crashes with AttributeError instead of usage](https://github.com/OpenMinion/openminion/issues/752) — missing: version / environment, reproduction steps

Next step: a maintainer reviews this draft before any label is applied.
