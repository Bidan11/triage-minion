# Triage Report

## Summary

| ID | Title | Category | Priority | Suggested Label | Missing Info |
|----|-------|----------|----------|-----------------|--------------|
| 752 | cli: bare `openminion replay` crashes with AttributeError instead of usage | bug | P1 | type:bug | version / environment, reproduction steps |
| 769 | [0.1.22] Runtime bootstrap fails on Windows (WinError 206) because browser-playwright artifact dirs are created under... | bug | P2 | type:bug | — |
| 766 | storage: empty storage.path ("") in agents.json resolves to data_root directory and fails with sqlite3.OperationalError | bug | P2 | type:bug | — |
| 754 | cli: `mcp import --from` reports a missing or malformed source file as an internal error | bug | P2 | type:bug | version / environment, reproduction steps |
| 759 | llm: add a provider cooldown registry and honour Retry-After instead of a constant retry backoff | feature | P2 | type:feature | — |
| 770 | [0.1.22] Agent.run(timeout_seconds=...) cannot extend the 300 s brain turn budget, and the budget stop is returned as... | bug | P2 | type:bug | — |
| 774 | [0.1.22] Handoff cannot bound or approve the delegated target run: build_delegate_tool calls target.run(message) with... | bug | P2 | type:bug | — |
| 757 | turn-input: an accepted `steer_current` is never applied or retired when its turn ends, and 20 of them wedge the sess... | bug | P3 | type:bug | version / environment, reproduction steps |
| 767 | cli: add `config diff` so an import can be previewed before it overwrites the config | feature | P3 | type:feature | — |
| 773 | [0.1.22] TurnResponse.telemetry reports 0 tokens when usage_*_tokens metadata keys are absent (no in-tree producer) | bug | P3 | type:bug | — |

## Top Priority Items

**P1 — Immediate attention**

- **#752** `cli: bare openminion replay crashes with AttributeError instead of usage` — A bare `replay` command crashes with an `AttributeError` rather than showing usage guidance. Missing: version/environment and reproduction steps.

**P2 — High priority**

- **#769** Runtime bootstrap fails on Windows (WinError 206) because browser-playwright artifact directories are created under an invalid path.
- **#766** Empty `storage.path` (`""`) in `agents.json` resolves to `data_root` and fails with `sqlite3.OperationalError`.
- **#754** `cli: mcp import --from` reports a missing or malformed source file as an internal error instead of a clear user-facing message. Missing: version/environment and reproduction steps.
- **#759** `llm: add a provider cooldown registry and honour Retry-After instead of a constant retry backoff` — Feature request for smarter retry handling.
- **#770** `[0.1.22] Agent.run(timeout_seconds=...) cannot extend the 300 s brain turn budget, and the budget stop is returned as...`
- **#774** `[0.1.22] Handoff cannot bound or approve the delegated target run: build_delegate_tool calls target.run(message) with...`

**P3 — Lower priority**

- **#757** `turn-input: an accepted steer_current is never applied or retired when its turn ends, and 20 of them wedge the sess...` — Missing: version/environment and reproduction steps.
- **#767** `cli: add config diff so an import can be previewed before it overwrites the config`
- **#773** `[0.1.22] TurnResponse.telemetry reports 0 tokens when usage_*_tokens metadata keys are absent (no in-tree producer)`

## Missing Information from Reporters

| Issue | Missing Info |
|-------|--------------|
| 752 | version / environment, reproduction steps |
| 754 | version / environment, reproduction steps |
| 757 | version / environment, reproduction steps |

## Counts

- Total issues: 10
- Bugs: 8 | Features: 2
- P1: 1 | P2: 6 | P3: 3