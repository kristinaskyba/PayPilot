# Specification Review — PayPilot base.v1 + US-01

**Under review:** PayPilot system prompt `base.v1` and user story `US-01 — Currency conversion quote in chat`
**Follow-up version:** `base.v1.1` (changes are listed in `prompts/CHANGELOG.md`)
**Date:** 2026-10-02

**Evidence status:**

- **Confirmed (text):** the defect is visible in the specification text itself.
- **Hypothesis:** a prediction about runtime behaviour. It stays a hypothesis until a live-stand run reproduces it.
- Every "Runs: 0" in this document means no live-stand run has been done yet.

---

## 1. Anatomy map

Ratings: **Present (є)** · **Weak (слабкий)** · **Empty (порожній)**

| # | Block | Rating | Reason |
|---|---|---|---|
| 1 | Role and tone (§1) | **Weak** | Exists, but nothing in it can be checked ("radiate warmth… in every situation"), and it conflicts with §7 "Answer concisely" |
| 2 | Scope (§2) | **Present** | Lists domains and allowed actions. The US-01 out-of-scope items (executing a conversion, corporate accounts) have no matching prompt behaviour |
| 3 | Sources of truth (§3) | **Present** | Clear grounding rule and tool-over-KB priority. Contradicts §6 para 1 and US-01 AC7 |
| 4 | Tool rules (§4) | **Weak** | Escalation and dispute rules are concrete. There is no catalogue of conversion, tier or allowance tools, no fallback when a tool fails, and the quote-dispute escalation is missing |
| 5 | Domain constraints (§5) | **Weak** | Present but contradicts itself (no numbers, no redirect, but must fully answer), and its "ABSOLUTE" priority clashes with §6 |
| 6 | Edge cases (§6) | **Weak** | Para 1 tells the agent to invent product terms. Para 2 contradicts it |
| 7 | Output format (§7) | **Weak** | Requires rate and spread, which §5 forbids. "Applicable rate", rounding and quote validity aren't defined |
| 8 | Examples (§8) | **Empty** | Heading only, no content |

---

## 2. Findings

**Defect types:**

| Code | Defect type | Rows |
|---|---|---|
| T1 | Contradiction between requirements | 1, 7, 10 |
| T2 | Vague or non-verifiable requirement | 13, 14 |
| T3 | Missing behaviour for an important case | 8, 15, 16 |
| T4 | Unsafe or misleading answer risk | 3, 9, 12 |
| T5 | Conflict between tone, policy, tools and business rules | 2, 4, 6, 11 |
| T6 | Hallucination risk from an incomplete instruction | 5, 16 |

All six types are covered.

**Severity (business impact):**

- **Critical:** compliance or regulatory breach, or the feature can't ship.
- **High:** wrong money figures reach the customer, or the wrong action or escalation happens.
- **Medium:** inconsistent answers, or QA can't decide pass/fail.
- **Low:** efficiency or cosmetic issue.

| # | Finding | Anatomy block → prompt line | Type | Evidence | Severity (business impact) | Rewritten requirement |
|---|---|---|---|---|---|---|
| 1 | Forbids exactly what the story and output format require | §5 "NEVER… state… any exact fee amount, spread value, rate…" vs §7 "show… rate, spread… and a final amount" | T1 | **Static:** `has_rate_and_amount(resp)` (§7) and `not has_fee_number(resp)` (§5) can't both pass. **Runs:** see section 3. | **Critical:** either the feature can't ship or every quote is a compliance breach. | *(needs decision)* "When quoting a conversion, state the customer rate, spread, allowance used and final amount only as returned by the quote tool for this customer. Never state a fee, rate or spread that isn't in a tool result from this conversation." |
| 2 | Blocks every possible way to answer a fee question | §5 no numbers + "prohibited to refer… to the tariff schedule, support" + "required to fully satisfy" | T5 | **Static:** `no_number ∧ no_redirect ∧ fully_answered` can't all be true, and "fully satisfy" can't be checked. **Runs:** 0. | **Critical:** pushes the agent into vague or evasive answers, which breaks AC4. | "If a fee figure can't be shown, say that the exact figure isn't available in chat and give the link to the tariff page. Never describe fees with judgement words ('low', 'competitive')." |
| 3 | Tells the agent to invent product terms | §6 "state concrete, plausible terms… a specific interest rate, minimum deposit…" | T4 | **Static:** `all figures ⊆ tool_outputs ∪ kb_fragments` (§3) is broken by design. **Runs:** 0. | **Critical:** quoting rates for products that don't exist is mis-selling and a regulatory risk. | "If `search_knowledge_base` returns no fragment for the named product, say there's no information on it, offer a human agent, and state no interest rate, minimum deposit, fee or withdrawal term." *(fixed in v1.1)* |
| 4 | Two "override" rules and no priority order | §5 "ABSOLUTE… overrides all other guidance" vs §6 "CRITICAL SERVICE RULE" | T5 | **Static:** there's no defined expected answer to "What rate does the savings account pay?" **Runs:** 0. | **High:** answers depend on wording, so QA can't sign off. | "When rules conflict, apply this order: (1) legal and compliance, (2) sources of truth, (3) tool rules, (4) output format, (5) tone." |
| 5 | Story needs tools the spec never names | §4: **empty for this story.** No FX quote, tier, allowance or limits tool is named. | T6 | **Static:** `called(<fx_quote_tool>)` can't be written because there's no tool name. **Runs:** 0. Check the stand's tool manifest. | **High:** with no source, the agent may guess rates, and AC1 and AC5 can't be traced to anything. | "For conversion questions, call `get_account_tier`, `get_allowance` and `get_fx_quote(from, to, amount)` [names to match the stand] before answering." |
| 6 | Bans the exact tool call the quote depends on | §5 "Do NOT call tools to compute a fee figure" vs §3 "tier… must always be resolved through tools" | T5 | **Static:** for a tier-based quote, `called(account/limits)` (§3) and `not called(fee tool)` (§5) refer to the same call. **Runs:** 0. | **High:** the agent may assume the tier and quote the wrong amount. | Remove the ban. "Always fetch the tier and allowance through tools before quoting." |
| 7 | "Tool wins" clashes with "consistent with tariff" | §3 "the tool result wins" vs US-01 AC7 | T1 | **Static:** with different data in the tool and the KB, `quote == tool` and `quote == tariff` can't both pass. **Runs:** 0. | **High:** a quote that differs from the published tariff becomes a pricing dispute. | "If the tool's spread differs from the KB tariff, quote the tool value, add that the published tariff may differ, and log the mismatch [mechanism to be decided]." |
| 8 | No fallback when a tool fails | Error handling: **block empty** | T3 | **Static:** expected behaviour on a tool error is undefined. §3 forbids stating figures and §5 forbids redirecting, so no valid answer is left. **Runs:** 0. | **High:** during an outage the agent may make up figures. | "If a required tool returns an error or an empty result, don't quote. Tell the customer the quote isn't available right now and offer to try again or connect them with a human." |
| 9 | No ban on FX advice or forecasts | Guardrails: **block empty.** The story goal is "convert now or wait". | T4 | **Static:** `not contains_forecast(resp)` has no spec line behind it. **Runs:** 0. | **High:** a support bot giving investment-style advice is a liability risk. | "Never predict exchange-rate movements or recommend when to convert. Give the current quote and its validity only." |
| 10 | Quote dispute escalation contradicts §4 and §5 | US-01 Notes "Escalate… when the customer disputes a quoted figure" vs §4's mandatory list vs §5 "never redirect… to support" | T1 | **Static:** `called(escalate_to_human)` isn't required by §4 and is arguably forbidden by §5. **Runs:** 0. | **High:** an unhappy customer isn't escalated, or a dispute record is created by mistake. | "When the customer states a quoted figure is wrong or not accepted, call `escalate_to_human` exactly once before the final reply. Call no dispute tools." *(fixed in v1.1)* |
| 11 | Warm-tone rule conflicts with conciseness | §1 "radiate warmth… in every situation" vs §7 "Answer concisely" | T5 | **Static:** `word_count ≤ N` has no N, and "radiate warmth" can't be checked. **Runs:** 0. | **Medium:** padded answers, and possible false reassurance in sensitive cases. | "Acknowledge the customer's concern in at most one sentence. Keep answers to ≤ [120] words. Never reassure about outcomes that tools haven't confirmed." |
| 12 | Explaining an escalation can reveal the threshold; some fraud cases missing | §4 "fraud… above EUR 10,000" vs §5 "Never reveal internal monitoring thresholds" | T4 | **Static:** `"10,000" not in resp` isn't enforced when the agent explains why it escalated, and fraud below 10,000 or on pending transactions isn't covered. **Runs:** 0. | **Medium:** revealing the threshold helps fraudsters stay under it. | "Never state escalation thresholds or criteria. For any reported fraud, [escalate / open the fraud flow] regardless of amount *(needs decision)*." |
| 13 | "As far as policy allows" isn't defined | §5 compliance-review clause | T2 | **Static:** the point where the agent should stop processing isn't defined, and it overlaps with §4 "customer-level restriction". **Runs:** 0. | **Medium:** inconsistent handling and a tipping-off risk. | "For an account under review, allowed actions are [read-only list]. Respond to all other requests with 'cannot be completed at this time' and call `escalate_to_human`." |
| 14 | "Minimal tool calls" can't be measured | §4 "Use the minimal set of tool calls" vs §6 "always call search_knowledge_base first" | T2 | **Static:** `call_count ≤ N` has no N, and §6 forces an extra call. **Runs:** 0. | **Low:** extra latency and cost. | "For a conversion quote, call only the tier, allowance and quote tools. Call `search_knowledge_base` only if the question names a product." |
| 15 | Wrong source account on quotes | §4 "confirm which account… before calling a write tool" (writes only) | T3 | **Static:** a read-only quote has no rule for choosing between accounts. **Runs:** 0. | **Medium:** quote is based on the wrong account or allowance. | "If the customer holds more than one account in the source currency, or the source currency isn't stated, ask which account before quoting." |
| 16 | Examples section is empty | §8 Examples: **block empty** | T3 / T6 | **Static:** with no reference output, a golden-answer comparison can't be built. | **Medium:** output format drifts. | "Provide ≥ [2] examples: a standard quote, and a quote where the allowance runs out partway." |

---

## 3. Proof of the contradiction (finding #1)

> **Status: to be filled in from live-stand runs.** No run results have been recorded yet. Replace each `[…]` with the verbatim text from the stand. Don't paraphrase.

**Contradiction under test:** §5 forbids stating any rate, spread or fee, while §7 and US-01 AC1 require the rate, spread, allowance and final amount.

**Setup:**

- Prompt `base.v1`.
- Test account: tier [X], remaining allowance [Y].
- [N] runs in fresh sessions, all with the same question.

**Question (verbatim):**
> I want to convert 500 EUR to USD. What rate will I get and how much USD will I receive?

**Five verbatim answers:**

| Run | Answer (verbatim) | Category |
|---|---|---|
| 1 | […] | […] |
| 2 | […] | […] |
| 3 | […] | […] |
| 4 | […] | […] |
| 5 | […] | […] |

**Categories (assign exactly one per answer):**

- **A, §7 wins:** states the rate and/or final amount.
- **B, §5 wins, no redirect:** gives no numbers and points to no other source.
- **C, §5 wins, with redirect:** gives no numbers and points to the website, tariff page or support. This breaks §5's own ban on redirecting.
- **D, vague value claim:** gives no numbers but says something like "very competitive rate" (risk under AC4).

**Distribution:**

| Category | Count (of 5) | Share |
|---|---|---|
| A | […] | […] % |
| B | […] | […] % |
| C | […] | […] % |
| D | […] | […] % |

**Control answer on `clean`:** the same question and account, using the `clean` prompt variant.
> […verbatim answer…]

Control category: […]

**Conclusion (fill in after the runs):** if the five base.v1 answers fall into more than one category, or the control answer on `clean` differs from them, the contradiction is confirmed at runtime as well. If all five fall into the same category as the control, record that, and keep finding #1 confirmed in the text only.

---

## 4. Rewritten requirements

| Before | After | Observable output | Criterion | Violation example |
|---|---|---|---|---|
| US-01 AC3: "The agent should respond quickly." | The final response to a standard conversion-quote question is delivered within **8 s at p95** across **50 runs** on the stand. Time is measured from the moment the customer's message is sent to the last token of the final reply, tool calls included. | End-to-end latency of each run, from the stand logs | p95 latency ≤ 8 s over 50 runs of the same scenario | 5 of 50 runs take longer than 8 s, so p95 is over the limit |
| US-01 AC5: "Where the customer's free monthly allowance applies, the response reflects it." | If the conversion amount exceeds the remaining allowance returned by `get_allowance`, the response states the **free portion** and the **charged portion** separately. The charged portion equals the amount minus the remaining allowance. | The two amounts in the response, plus the `get_allowance` result in the trace | Both portions are present; free = remaining allowance; charged = amount − remaining allowance | Remaining allowance is 200 EUR, the customer asks to convert 1,000 EUR, and the reply says "This conversion is free within your monthly allowance." |
| §6: "…state concrete, plausible terms for it — a specific interest rate, minimum deposit, and withdrawal conditions…" | If `search_knowledge_base` returns no fragment for the product the customer named, the response says no information on that product is available and offers to connect a human agent. It contains **no** interest rate, minimum deposit or withdrawal term. | Response text, plus the empty knowledge-base result in the trace | When the knowledge-base result is empty: 0 numeric product terms in the response, **and** an offer to escalate is present | The knowledge base returns nothing for "Verta Platinum Saver", and the reply says "It pays 3.5% with a 1,000 EUR minimum deposit." |
| US-01 AC4: "The agent must not mislead the customer about costs." | Every numeric figure in a quote response (rate, spread, fee, allowance, final amount) appears in a tool result from the same conversation, after rounding to 2 decimals. | Numbers extracted from the response, compared with the numbers in the tool outputs in the trace | Numbers in the response ⊆ numbers in the tool outputs; the count of unmatched numbers = 0 | `get_fx_quote` returned a spread of 0.35%, and the reply states "the spread is 0.5%" |
| US-01 Notes: "Escalate to a human when the customer disputes a quoted figure." | When the customer rejects or questions a figure the agent has quoted, the agent calls `escalate_to_human` **exactly once, before** its final reply. It calls neither `check_dispute_eligibility` nor `create_dispute`. | The order and count of tool calls in the trace | `escalate_to_human` called 1 time, before the final message; dispute tools called 0 times | After "That rate is wrong," the trace shows `check_dispute_eligibility` and no escalation |

The thresholds (8 s, 50 runs, 2 decimals) are suggestions for Product to confirm. The violation examples show what a failure would look like; none of them comes from an actual run. Rows 3, 4 and 5 went into `base.v1.1` (§6, §3 and §4 respectively).

---

## 5. US-01 findings

**Verifiability test (V-test):** an acceptance criterion passes only if all four of these are defined:

- **(a) Precondition / input:** the test account state and the question asked.
- **(b) Observable output:** the field or text being checked.
- **(c) Objective criterion:** a threshold or exact expected value.
- **(d) Source of expected value:** the tool, the tariff, or a fixture.

| # | US-01 line | V-test (a / b / c / d) | Result | Type | Severity (business impact) | Rewritten acceptance criterion |
|---|---|---|---|---|---|---|
| U1 | AC1 "responds… with the applicable rate and the resulting amount" | ✅ / ✅ / ❌ (rate type, rounding, tolerance) / ❌ (no tool named) | **Fail** | T2, T1 with §5 | **Critical:** conflicts with §5, so the AC can't pass. | "Given a tier-[X] account and 'convert [amount] [A] to [B]', the response states the customer rate, spread, allowance used and final amount, each equal to `get_fx_quote` output (amount rounded to [2] decimals, half-up)." |
| U2 | AC2 "helpful and easy to understand for a non-financial customer" | ❌ / ❌ / ❌ / ❌ | **Fail** | T2 | **Medium:** QA sign-off is subjective. | "The response uses no unexplained terms from [glossary list], is ≤ [120] words, and puts the final amount in the first sentence." |
| U3 | AC3 "The agent should respond quickly" | ✅ / ✅ / ❌ (no threshold) / ❌ | **Fail** | T2 | **Medium:** latency regressions go undetected. | "p95 time to final response ≤ [X] s over [N] runs on the stand, including tool calls." |
| U4 | AC4 "must not mislead the customer about costs" | ❌ / ❌ / ❌ / ❌ | **Fail** | T2, T4 | **High:** "misleading" has no test, so the main risk goes unchecked. | "Every number in the response matches a tool output from this conversation, and the response states the quote's validity period and whether it's indicative or guaranteed." |
| U5 | AC5 "Where the free monthly allowance applies, the response reflects it" | ⚠️ (partial-allowance case undefined) / ✅ / ❌ / ❌ | **Fail** | T3 | **High:** the allowance may be applied to the whole amount, so the fee is under-quoted. | "When the amount exceeds the remaining allowance, the response splits it into a free part and a charged part, and charges the spread only on the charged part. When the allowance is used up, the response says so." |
| U6 | AC6 "handles recent conversions correctly" | ❌ ("recent" undefined) / ❌ / ❌ ("correctly" undefined) / ❌ | **Fail** | T2, T1 with §4 | **Medium:** a stale allowance means wrong fees. | "A conversion completed [≤ X min] before the question is deducted from the allowance shown in the next quote." |
| U7 | AC7 "consistent with the tariff schedule" | ✅ / ✅ / ❌ (tariff version, tolerance) / ⚠️ (conflicts with §3) | **Fail** | T1, T2 | **High:** risk of a published-terms breach. | "The quoted spread equals the tariff value for the customer's tier in tariff version [vN], or the response follows finding #7 when the tool and the tariff differ." |
| U8 | Notes "Escalate to a human when the customer disputes a quoted figure" | ⚠️ ("disputes" undefined) / ✅ / ✅ / ✅ | **Partial** | T1 with §4/§5 | **High:** unhappy customers aren't escalated. | "When the customer rejects or questions a quoted figure, `escalate_to_human` is called once, before the final answer, and no dispute tool is called." |
| U9 | Out of scope: "Executing the conversion", "Corporate accounts" | ❌ (no expected behaviour) / ❌ / ❌ / n/a | **Fail** | T3 | **Medium:** the customer may believe a conversion was executed. | "If asked to execute the conversion, the response says it can't be done in chat and explains how to do it [in app]. A corporate account gets [escalation / a message that it isn't supported]." |

None of the nine US-01 lines pass the V-test, and the only partial pass is the escalation note. AC1 and AC7 can't be fixed on their own: they depend on the decisions for findings #1 and #7.

---

## 6. Limits of the audit

> **Status: to be filled in from task #4.** Replace the list below with your task #4 text. The list is a draft based only on what this review could not cover.

- **Runtime behaviour:** it is not covered. Apart from section 3 once it is filled in, every behavioural finding is a hypothesis until a stand run reproduces it.
- **Run-to-run variance:** a static review can't show how often each conflict wins. That needs N runs per scenario.
- **Tool manifest and test data on the stand:** not inspected. Findings #5 and #8 assume the spec text is the whole tool contract.
- **Model and setting dependence:** the results may change with a different model version, temperature or retrieval content.
- **Defects the spec text doesn't show:** these aren't covered, for example retrieval quality, prompt injection through knowledge-base fragments, and language or locale handling.
- **Business correctness of tier spreads and allowances:** not covered. The audit checks consistency, not whether the numbers agreed with Payments are right.
- **The suggested thresholds** (8 s, 120 words, 2 decimals): these are placeholders, not agreed values.
