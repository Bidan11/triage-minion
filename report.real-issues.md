# Triage Report

Source: `real_issues.json` - 10 issue(s) triaged.

| # | Issue | Category | Priority | Missing info | Suggested label |
|---|-------|----------|----------|--------------|-----------------|
| 774 | [0.1.22] Handoff cannot bound or approve the delegated target run: build_delegate_tool calls target.run(message) with no timeout or approval_callback | bug | P2 | - | `type:bug` |
| 773 | [0.1.22] TurnResponse.telemetry reports 0 tokens when usage_*_tokens metadata keys are absent (no in-tree producer) | bug | P3 | - | `type:bug` |
| 770 | [0.1.22] Agent.run(timeout_seconds=...) cannot extend the 300 s brain turn budget, and the budget stop is returned as a normal reply | bug | P2 | - | `type:bug` |
| 769 | [0.1.22] Runtime bootstrap fails on Windows (WinError 206) because browser-playwright artifact dirs are created under the CWD even when no browser tool is used | bug | P2 | - | `type:bug` |
| 767 | cli: add `config diff` so an import can be previewed before it overwrites the config | feature | P3 | - | `type:feature` |
| 766 | storage: empty storage.path ("") in agents.json resolves to data_root directory and fails with sqlite3.OperationalError | bug | P2 | - | `type:bug` |
| 759 | llm: add a provider cooldown registry and honour Retry-After instead of a constant retry backoff | feature | P2 | - | `type:feature` |
| 757 | turn-input: an accepted `steer_current` is never applied or retired when its turn ends, and 20 of them wedge the session queue (QUEUE_FULL) | bug | P3 | version / environment, reproduction steps | `type:bug` |
| 754 | cli: `mcp import --from` reports a missing or malformed source file as an internal error | bug | P2 | version / environment, reproduction steps | `type:bug` |
| 752 | cli: bare `openminion replay` crashes with AttributeError instead of usage | bug | P1 | version / environment, reproduction steps | `type:bug` |

Next step: a maintainer reviews this draft before any label is applied.
