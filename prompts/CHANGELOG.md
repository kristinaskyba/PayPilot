# PayPilot prompt CHANGELOG

## v1.0 — baseline audit

Known defects: contradiction on fee disclosure, unverifiable tone requirement, no instruction for missing-data case.

Not measured: frequency of occurrence.

# Changelog — PayPilot system prompt

All changes to the PayPilot system prompt are recorded here. The original
`prompts/base.v1.md` is never edited; each new version is a new file.

## v1.1 — 2026-10-02

File: `base.v1.1.md` (copy of `base.v1.md` with the additions below).
Source: Specification Review — PayPilot. Every change refers to a finding
that was reproduced on the stand. No new requirement was added without an
observable output and a pass criterion.

### Added

- **Block 1 (Role and tone):** rule for answers to problem reports — first
  sentence names the problem, second sentence states the next action; no
  opening praise of the question. Replaces the unverifiable lesson-01 wording
  "Be deeply empathetic…" with a testable rule (review finding 5, R1).
- **Block 2 (Scope):** the agent cannot execute conversions or transfers, block
  or replace cards, or change limits, and must not offer to. (Findings 8, U5.)
- **Block 3 (Sources of truth):** customer-specific data only for the customer
  ID the customer gave for themselves; refuse third-party requests.
  (Finding 13. Note: this does not add real identity verification, which needs
  a tool the stand does not have.)
- **Block 6 (Edge cases):** a knowledge-base fragment is evidence about a
  product only if it names that product; otherwise say no such product was
  found. (Findings 3, 4.)
- **Block 6 (Edge cases):** lost / stolen card case — escalate, give the
  escalation ID, say the card must be blocked. (Finding 7.)
- **Block 7 (Output format):** fixed order and arithmetic rule for conversion
  quotes; explain "spread" on first use. (Findings 9, U3, U4; R3.)
- **Block 8 (Examples):** three examples with placeholders: lost card, unknown
  product, request to execute a conversion. (Finding 6.)

### Unchanged

- Blocks 4 and 5 are identical to v1.0.
- The lesson-01 overlay (D01, D02, D03) is not part of this version; its fee
  ban (block 5) and invented-product rule (block 6) are rejected per findings
  1, 2, 3 and 10.

### To verify

- Re-run the review questions against v1.1 on the stand before release
  (see `prompt-governance-policy.md`, Definition of done).

## v1.0

File: `prompts/base.v1.md`. Initial PayPilot system prompt as provided in the
stand repository. Eight blocks; block 8 (Examples) empty.
