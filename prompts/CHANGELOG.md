# PayPilot prompt CHANGELOG

## v1.0 — baseline audit

Known defects: contradiction on fee disclosure, unverifiable tone requirement, no instruction for missing-data case.

Not measured: frequency of occurrence.

## base.v1.1 — 2026-10-02

- **Version:** base.v1.1 (from base.v1)
- **Owner:** [owner]
- **Reviewer:** [reviewer]

### What changed

1. **§3 Sources of truth.** Replaced "If a figure (fee, rate, limit, date) is
   not present in a tool result or a retrieved fragment, do not state it" with
   a rule that every number in a response (fee, rate, spread, limit, amount,
   date) must appear in a tool result or retrieved fragment from the same
   conversation, with rounding to 2 decimals allowed.
2. **§4 Tool rules.** Added: when the customer states that a quoted figure is
   wrong or that they do not accept it, call `escalate_to_human` exactly once
   before the final reply, and call neither `check_dispute_eligibility` nor
   `create_dispute`.
3. **§6 Edge cases.** Removed the "CRITICAL SERVICE RULE" paragraph, which told
   the agent to state plausible product terms. Replaced it with: if
   `search_knowledge_base` returns no fragment for the named product, say there
   is no information on it, offer a human agent, and state no interest rate,
   minimum deposit, fee or withdrawal term.

No other text was changed. The header was updated to base.v1.1.

### Reason

- Change 1 closes audit finding #4 / US-01 AC4. "Must not mislead" and
  "figure… not present" could not be checked as a set comparison against tool
  outputs.
- Change 2 closes audit finding #10 / U8. The quote-dispute escalation existed
  only in the US-01 Notes, not in the prompt, and "dispute" could trigger the
  payment-dispute flow.
- Change 3 closes audit finding #3 (Critical). §6 told the agent to fabricate
  product terms, contradicting §3.

### Evidence

- **Static verifiability test** (precondition / observable output / objective
  criterion / source of expected value) applied to each new line:

  | Change | Precondition                                                         | Observable output                                                  | Criterion                                                                              | Source | Result |
  | ------ | -------------------------------------------------------------------- | ------------------------------------------------------------------ | -------------------------------------------------------------------------------------- | ------ | ------ |
  | 1 (§3) | Any conversation with numbers in the reply                           | Numbers in the reply; tool and knowledge-base outputs in the trace | Numbers in the reply ⊆ numbers in tool/KB outputs (±2-decimal rounding); unmatched = 0 | Trace  | Pass   |
  | 2 (§4) | Agent has quoted a figure; customer says it is wrong or not accepted | Tool-call order and count in the trace                             | `escalate_to_human` = 1, before the final message; dispute tools = 0                   | Trace  | Pass   |
  | 3 (§6) | `search_knowledge_base` returns no fragment for the named product    | Reply text; knowledge-base result in the trace                     | 0 numeric product terms in the reply, and an offer of a human agent is present         | Trace  | Pass   |

- **Runs:** 0. No live-stand runs have been done for v1.1.

### Not measured

- How the agent behaves at runtime on the stand with any of the three changes;
  no before/after comparison against v1.
- Regressions in unrelated scenarios (fraud escalation, statements, payment
  disputes, compliance review).
- **Known conflicts left unresolved:**
  - §5 still forbids stating any fee, rate or spread, which contradicts §7 and
    US-01 AC1 (finding #1).
  - §5's ban on referring customers to "support" may conflict with the
    human-agent offer in change 3 and with the escalation in change 2
    (findings #2, #10).
- Not tested: whether the trigger in change 2 ("states that a figure… is
  wrong, or that they do not accept it") catches paraphrases, partial
  disagreement, or questions about how a figure was calculated.
- Not changed in this version: latency (AC3), allowance split (AC5), FX-advice
  guardrail, tool-failure fallback, the empty §8 Examples.
