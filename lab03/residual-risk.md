# Residual risk: L03 golden set

Set: `golden.jsonl`, 34 cases, `set_hash` 0cdf2f682dad. Daily gate 29 cases, release gate 5 (human tone cases).

## Coverage matrix

| Layer | Engine oracle | Corpus oracle | Human oracle |
| --- | --- | --- | --- |
| action (tool called with right result) | 3 cases (L1 flag, L2 numeric) | - | - |
| generation (what the bot says) | 23 cases (L2 numeric, L3 contains, L4 must-not-say) | 3 cases (L3, L4) | 5 cases (L7 judge, release gate) |
| retrieval | not covered | not covered | not covered |
| memory | not covered | not covered | not covered |

Daily gate: 29 cases. Ladder levels used: 1, 2, 3, 4, 7. Severity: 6 critical, 25 high, 2 medium, 1 low.

## Failure classes and decisions

1. **Tone and wording changes.** Evidence: the prompt-change run (apology line) was seen by only 1 of 29 cases (FX-003-S, a "contains" check). Numbers and "must not say" checks cannot see tone. Decision: **accept** for the daily gate. The 5 human tone cases in the release gate cover it, and a judge on every daily run costs more than the risk is worth.
2. **Complaints that could not be turned into a case** (C-02, C-15, C-20). C-02 has no customer and no question we can replay, C-20 has no name, date or answer text, and C-15 is a mobile app freeze, not the bot. Without something to replay there is no oracle. Decision: **defer** C-02 and C-20 until more detail arrives; C-15 is **accepted** here as out of scope for the bot (passed to the app team).
3. **Retrieval and memory failures** (C-13, C-14 retrieval; C-18 memory). The set has no cases on these layers. Decision: **defer** to L04 (retrieval) and L05 (memory).

## Size and cost

- Daily run: 29 cases x 1 run = 29 bot calls, about 145,000 tokens and about 100 s (clean run: 144,710 tokens, 96.5 s).
- Release run: adds 5 human cases x 5 runs = 25 judged runs, so it is slower and costs more. Run it before a release, not on every change.
- Sensitivity: the prompt-change test moved 1 of 29 cases (FX-003-S); the defective profile moved 15 of 29. The set is sensitive to wrong numbers and wrong rules, and much less to phrasing.
- Single runs: each daily case runs once, so a lone failure like FX-003-S can be noise. A control re-run (as done here) is the cheap way to check.
