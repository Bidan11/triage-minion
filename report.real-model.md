# Triage Report — 10 loaded issues

**Snapshot:** 18 Nov 2026 · 10 issues (8 bug, 2 feature) · Priorities: 1 × P1, 6 × P2, 3 × P3

## Summary table

| # | ID | Title | Category | Priority | Missing info |
|---|----|-------|----------|----------|--------------|
| 1 | 752 | cli: bare `openminion replay` crashes with AttributeError instead of usage | bug | **P1** | version / environment, reproduction steps |
| 2 | 759 | llm: add a provider cooldown registry and honour Retry-After instead of a constant retry backoff | feature | P2 | — |
| 3 | 766 | storage: empty `storage.path` ("") in agents.json resolves to data_root directory and fails with sqlite3.OperationalError | bug | P2 | — |
| 4 | 769 | Runtime bootstrap fails on Windows (WinError 206) because browser-playwright artifact dirs are created under long paths | bug | P2 | — |
| 5 | 770 | `Agent.run(timeout_seconds=...)` cannot extend the 300 s brain turn budget, and the budget stop is returned as... | bug | P2 | — |
| 6 | 774 | Handoff cannot bound or approve the delegated target run: `build_delegate_tool` calls `target.run(message)` with... | bug | P2 | — |
| 7 | 754 | cli: `mcp import --from` reports a missing or malformed source file as an internal error | bug | P2 | version / environment, reproduction steps |
| 8 | 757 | turn-input: an accepted `steer_current` is never applied or retired when its turn ends, and 20 of them wedge the session | bug | P3 | version / environment, reproduction steps |
| 9 | 773 | TurnResponse.telemetry reports 0 tokens when `usage_*_tokens` metadata keys are absent (no in-tree producer) | bug | P3 | — |
| 10 | 767 | cli: add `config diff` so an import can be previewed before it overwrites the config | feature | P3 | — |

## Top priority items

**1. #752 — P1 / bug — Bare `openminion replay` crashes with AttributeError**
Highest-severity item in the batch: a plain CLI invocation dies with an unhandled AttributeError rather than printing usage. Any user hitting the command gets a traceback instead of guidance, so this should be fixed first. Needs the reporter's environment details and exact invocation to confirm scope.

**2. #774 — P2 / bug — Handoff cannot bound or approve the delegated target run**
`build_delegate_tool` invokes `target.run(message)` without a way to bound or approve the delegated run. This is a delegation-safety gap: a sub-run can escape the parent's control envelope. Worth handling alongside #770, since both concern run-budget enforcement.

**3. #770 — P2 / bug — `Agent.run(timeout_seconds=...)` cannot extend the 300 s brain turn budget**
The per-run timeout cannot override the fixed 300-second turn budget, and the budget stop surfaces as the wrong kind of result. Callers have no reliable way to ask for a longer turn or to distinguish "timed out" from other stops.

**4. #769 — P2 / bug — Windows bootstrap fails (WinError 206) on long browser-playwright artifact paths**
Path-length failure at bootstrap blocks the runtime entirely on Windows — a hard platform break rather than a degraded path. Fix is likely a shorter artifact root or extended-path handling.

**5. #766 — P2 / bug — Empty `storage.path` resolves to the data_root directory and fails with sqlite3.OperationalError**
An empty string is accepted as a path and resolved to a directory, so the failure arrives later as an opaque sqlite error. Validation at config-load time would convert this into a clear message.

**6. #759 — P2 / feature — Provider cooldown registry honouring Retry-After**
Current behaviour retries on a constant backoff and ignores server-provided Retry-After; a cooldown registry would stop hammering throttled providers and reduce cascading failures.

**7. #754 — P2 / bug — `mcp import --from` misreports missing/malformed source files as internal errors**
User input errors are being surfaced as internal errors, which hides the actionable cause and inflates apparent severity.

Lower priority: **#757** (P3, `steer_current` never retired and 20 stacked entries wedge the session — a real wedge risk but narrow), **#773** (P3, telemetry reports 0 tokens when the metadata keys have no in-tree producer), **#767** (P3, feature: `config diff` preview before an import overwrites config).

## Missing information from reporters

Three issues still lack details needed to reproduce and scope:

- **#752** (P1) — version / environment, reproduction steps
- **#754** (P2) — version / environment, reproduction steps
- **#757** (P3) — version / environment, reproduction steps

For each of these we need: the exact release/build, OS and Python version, the precise command or config that triggered the failure, and the full traceback or log excerpt. **#752 is the priority ask** — it is the only P1 in the batch and cannot be confirmed as isolated versus systemic without its environment.

The remaining seven issues carry enough detail to investigate as filed.
