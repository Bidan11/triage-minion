# Triage Report

## Summary Table

| ID | Title | Category | Priority | Missing Info | Suggested Label |
|----|-------|----------|----------|--------------|-----------------| 
| 774 | [0.1.22] Handoff cannot bound or approve the delegated target run: build_delegate_tool calls target.run(message) with no timeout or approval_callback | bug | P2 | [] | type:bug |
| 773 | [0.1.22] TurnResponse.telemetry reports 0 tokens when usage_*_tokens metadata keys are absent (no in-tree producer) | bug | P3 | [] | type:bug |
| 770 | [0.1.22] Agent.run(timeout_seconds=...) cannot extend the 300 s brain turn budget, and the budget stop is returned as a normal reply | bug | P2 | [] | type:bug |
| 769 | [0.1.22] Runtime bootstrap fails on Windows (WinError 206) because browser-playwright artifact dirs are created under the CWD even when no browser tool is used | bug | P2 | [] | type:bug |
| 767 | [0.1.22] cli: add `config diff` so an impor... | bug | ? | [] | type:bug |

## Top Priority Items (P1)

No P1 issues found in the loaded set.

## Top Priority Items (P2)

1. **[774] [0.1.22] Handoff cannot bound or approve the delegated target run: build_delegate_tool calls target.run(message) with no timeout or approval_callback**
   - Category: bug
   - Missing Info: None
   - Suggested Label: type:bug

2. **[770] [0.1.22] Agent.run(timeout_seconds=...) cannot extend the 300 s brain turn budget, and the budget stop is returned as a normal reply**
   - Category: bug
   - Missing Info: None
   - Suggested Label: type:bug

3. **[769] [0.1.22] Runtime bootstrap fails on Windows (WinError 206) because browser-playwright artifact dirs are created under the CWD even when no browser tool is used**
   - Category: bug
   - Missing Info: None
   - Suggested Label: type:bug

## Top Priority Items (P3)

1. **[773] [0.1.22] TurnResponse.telemetry reports 0 tokens when usage_*_tokens metadata keys are absent (no in-tree producer)**
   - Category: bug
   - Missing Info: None
   - Suggested Label: type:bug

2. **[767] [0.1.22] cli: add `config diff` so an impor...**
   - Category: bug
   - Priority: Unknown (likely P2-P3 based on truncation)
   - Missing Info: None
   - Suggested Label: type:bug

## Missing Information from Reporters

Based on the loaded issues, no specific missing information has been reported for any of the issues. All issues have empty missing_info arrays.

## Issue Details Summary

The loaded issues primarily concern:
- Handoff and delegation mechanics (P2)
- Timeout and budget management (P2)
- Windows runtime bootstrap issues (P2)
- Telemetry reporting (P3)
- CLI configuration features (priority unclear)

All issues are categorized as bugs, with most being P2 priority affecting core functionality.