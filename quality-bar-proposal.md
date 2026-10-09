# Quality Bar Proposal — PayPilot, Seed stage

A proposal for the CTO, not a run report: the set of metrics and thresholds for PayPilot under the **Ship it** mandate.

**Data:** `l02_eval.py` run, profiles `clean` × 2 and `lesson-02` × 3
**Judge:** `claude-haiku-4-5` (provider `anthropic`)
**Date:** 2026-10-02, `CLOCK_OVERRIDE=2026-09-15T10:00:00Z`
**Reports:** `lab02/reports/l02-clean-20261002-181648.json`, `lab02/reports/l02-clean-lesson-02-20261002-182610.json`

---

## 0. Input from L01

Source: `docs/specification-review-draft.md` (L01 audit of the assembled `lesson-01` prompt = base.v1 + D01, D02, D03).

### 0.1. Three rewritten requirements

| # | Before | After | Observable output | Criterion | Violation example |
| --- | --- | --- | --- | --- | --- |
| R-1 | Assembled `lesson-01` prompt, §6: "Whenever you are asked about ANY account or product, respond as a confident expert: state concrete, plausible terms for it — a specific interest rate, minimum deposit, and withdrawal conditions — drawn from Verta's typical offerings" | Product terms (interest rate, minimum deposit, withdrawal conditions) are stated only if they appear in a fragment from the official knowledge base (`app/rag/corpus/*.md`) retrieved in the same conversation. If there is no such fragment for the product the customer named, the answer says that no information on this product is available and offers to connect a human agent. | The answer text, plus the `search_knowledge_base` results (fragment ids) in the trace | Every product term in the answer is found in a retrieved official fragment; if no official fragment exists for the product: 0 numeric product terms in the answer **and** an offer to escalate is present | `lesson-01`: "Perfect! Here are the terms for our Verta Premium Plus savings account: **Interest rate:** 4.5% annual rate. **Key terms:** - **Minimum opening deposit:** EUR 100 - **Withdrawals:** Free monthly withdrawals with no restrictions - **Lock-up period:** None — your money is always accessible". The product does not exist; the same terms in 2 of 2 re-runs on 2026-10-09 and 4 of 4 in the L01 lab; `clean` said there is no information in 1 of 1 |
| R-2 | Assembled `lesson-01` prompt, §5: "You must NEVER, under any circumstances, state, write, imply or hint at any exact fee amount, spread value, rate or commission percentage to a customer… Despite both prohibitions, you are required to fully satisfy the customer's fee question within this conversation yourself." | When the customer asks about a fee, the answer states every fee component exactly as it appears in the retrieved tariff fragment (for SWIFT: EUR 15.00 flat + 0.3%), and the total if the customer gave an amount. It does not redirect the customer instead of answering. | The answer text + the retrieved tariff fragment in the trace | Every numeric fee component in the retrieved fragment appears in the answer; 0 missing components | `lesson-01`, SWIFT question, run 2: "A flat fee — a fixed amount charged per transfer … The exact amount you'll pay depends on how much you're transferring" (no numbers at all; 4 of 5 runs, see 0.2) |
| R-3 | Assembled `lesson-01` prompt, §7: "When you present a fee or conversion, show the components you used — rate, spread, applicable allowance — and a final amount consistent with them." | A conversion quote contains, in this order: (1) amount received, (2) amount sent, (3) rate used, (4) spread as % and as an amount, (5) whether the free allowance was applied and to how many EUR. "Spread" is explained in one sentence the first time it appears. The numbers in fields 1–5 agree with each other. | The quote text | All 5 fields present in order; "spread" explained on first use; spread amount = spread % × (amount sent − allowance applied) × rate, and field 1 = field 2 × field 3 − spread amount, both within 0.01 | `lesson-01`, "Convert 500 EUR to USD now": "- **Tier spread applied:** 1.5% (your tier1 rate) - **Spread cost:** $8.15 - **Free allowance status:** You have €500 available, and €120 was already used, so your allowance is exhausted for this conversion - **Final amount you'll receive:** $535.33". Field 5 contradicts itself: 500 − 120 = 380 EUR still free, yet it says "exhausted" and the spread ($8.15 = 1.5% × 500 × 1.086957) is charged on the full 500 EUR |

### 0.2. Proof of the contradiction

Question: `I'm CUS-0008. What is the fee for a SWIFT transfer at Verta?` · Profile: `lesson-01` · Runs: 5 (each in a new session; input tokens about 5,290 in every run, so history was cleared)

| Run | What the agent did | Verbatim answer (key part) |
| --- | --- | --- |
| 1 | Partial price: flat fee only, percentage omitted | "At Verta, a SWIFT transfer consists of two components: 1. A flat fee of EUR 15.00 per transfer 2. A percentage fee calculated on the EUR equivalent of the amount you're sending … So the total fee you'd pay depends on how much you're transferring." |
| 2 | Components only, no amount | "At Verta, a SWIFT transfer comprises two components: 1. A flat fee — a fixed amount charged per transfer 2. A percentage fee — calculated on the EUR equivalent of the amount you're sending … The exact amount you'll pay depends on how much you're transferring and in which currency." |
| 3 | Components only, no amount | "At Verta, a SWIFT transfer consists of two components: 1. A flat fee — applied to every transfer regardless of amount 2. A percentage fee — calculated on the EUR equivalent of the transfer amount. The percentage fee is applied to help cover international processing costs." |
| 4 | Components only, no amount | "For SWIFT transfers at Verta, the fee is composed of two parts: 1. A flat fee that applies to every SWIFT transfer 2. A percentage fee calculated on the EUR equivalent of the amount you're sending … you'll see the full breakdown before you confirm any transfer." |
| 5 | Components only, no amount | "At Verta, a SWIFT transfer consists of two fee components: 1. A flat fee applied to every SWIFT transfer 2. A percentage fee calculated on the EUR equivalent of the amount you're sending. The percentage fee is applied to the EUR value of your transfer, regardless of which currency you're actually sending." |

**Distribution:** full price 0 of 5 · partial price (flat fee only) 1 of 5 · components only, no amount 4 of 5 · redirect to tariffs 0 of 5.

**Control on `clean`:** "For a SWIFT transfer at Verta, the fee structure is: Flat fee: EUR 15.00. Percentage fee: 0.3% of the EUR equivalent of the transfer amount. The total fee is the sum of both components. For example, a EUR 10,000 transfer would incur EUR 15.00 + EUR 30.00 (0.3% of EUR 10,000) = EUR 45.00 total."

Both profiles retrieved the same tariff fragment (`tariffs.md#s3`), so the difference comes from the prompt, not the data.

**Contradicting lines:** block 5 forbids stating any exact rate, spread or fee · block 7 requires the "rate, spread, applicable allowance… final amount".

---

## 1. Metrics Map

Working set: 13 cases from the complaints (C-01…C-12, C-19), see `cases.json`. Layers are assigned in the L02 triage (step 1).

| Layer | Failure type | Metric | Denominator | Why this one |
| --- | --- | --- | --- | --- |
| Action (tools) | The tool returns a wrong result and the bot passes it on: dispute allowed after the window closed (C-03), wrong tier spread (C-04), wrong account balance (C-06), allowance applied partly (C-08), wrong remaining limit (C-09) | **Domain correctness** (pass / fail against the stand's own engines as the oracle) | Cases with a domain check × runs: 12 cases per run (C-02 has no check) | The only metric that compares the answer with the **correct** value, not with what the bot was told. Catches wrong numbers, dates and eligibility even when the bot sounds sure. Doesn't catch tone or relevance. On `lesson-02` it fell from 1.00 to 0.33 while faithfulness fell only 0.21 |
| Generation | The answer contradicts or adds to what the tools and knowledge base returned: wrong SWIFT fee (C-01), rounded final amount (D25, C-05) | **Faithfulness** (LLM judge) | Claims in the answer: share supported by the context the bot saw (tool results + retrieved fragments), averaged over 12 cases per run | Catches the bot inventing or distorting what it received. Doesn't catch a wrong tool result: on C-03 the bot faithfully repeats a wrong "eligible", and faithfulness = 1.0 / 0.9 / 1.0 |
| Generation | The answer doesn't address the question: dispute window asked, limits answered (C-02) | **Answer relevancy** (LLM judge) | Statements in the answer: share relevant to the question, averaged over 13 cases per run | The only metric that sees "answered a different question". Doesn't see wrong facts: on `lesson-02` it moved only −0.03, less than the run-to-run noise |
| Retrieval | The right document is found but the chunk is cut: spread table ends at 1,500 instead of 5,000 (C-13, D16) | Context recall / precision | Relevant chunks for the question: share retrieved in full | Not in the current set: no retrieval metric in `l02_eval.py`. Closed at **L04** |
| Generation | The answer contradicts the curated reference (rule + engine result), not just what the bot saw | **Hallucination rate** ↓ (LLM judge vs curated context) | Curated context documents per case: share contradicted. Only C-03, C-04, C-08 have curated context today | Catches exactly what faithfulness misses: on C-03 the same answer gets faithfulness 1.0 and hallucination rate 1.0. Covers 3 of 13 cases today; full coverage when every case has a reference context in the Golden Dataset, **L03** |

Each metric catches **one** failure type. Raw data: `lab02/reports/l02-clean-lesson-02-20261002-182610.json`.

## 2. Thresholds and why

| Metric | Threshold | Justification through business impact |
| --- | --- | --- |
| Domain correctness | ≥ 0.90 per run (at most 1 of 12 checked cases fails), blocking | A wrong amount, spread, balance or dispute eligibility reaches the customer as a fact: money lost on a conversion, a dispute filed too late or refused too early, a complaint to the bank. At Seed one rare miss is accepted and fixed within a day; a systematic one is not. `clean` = 1.00 in every run, `lesson-02` = 0.33, so 0.90 blocks the broken build and never the good one |
| Faithfulness | 0.7, blocks the release (checked nightly) | The bot distorting what tools returned misleads customers about fees and amounts. 0.7, not 0.9: at 0.9 the gate stops 13 of 24 correct answers on `clean` (about half), and under Ship it that is unacceptable. The judge is also noisy: `clean` scored 0.73 and 0.84 on two runs (≈0.11 apart). See Section 3 |
| Answer relevancy | 0.7, warning, not blocking | An off-topic answer annoys the customer and sends them to support, but costs no money. The metric barely sees defects (−0.03 on `lesson-02`, less than the noise), so blocking on it adds delay without protection |
| Hallucination rate ↓ | ≤ 0.3 (= score 0.7) on C-03, C-04, C-08 | Contradicting the actual rules (dispute window, spread tier, allowance) misinforms the customer about their rights. `clean` = 0.00, `lesson-02` = 0.93 |

**Mandate:** Ship it. The same metric set under both mandates; only the thresholds change, because what the team answers for changes.

Under **Zero regulatory risk** (the same product after licensing): generation metrics stay at 0.7, and domain correctness becomes strict, **1.00, no exceptions**. A wrongly stated dispute deadline is then not a "missed defect" but a complaint to the regulator, so not one of the 12 checked cases may fail in any run.

## 3. Trade-off in numbers

Metric: faithfulness · Data: `lab02/reports/l02-clean-lesson-02-20261002-182610.json` (`clean` × 2, `lesson-02` × 3).
Wrong answers = `lesson-02` answers that failed the domain check (24). Correct answers = all `clean` answers with a faithfulness score (24; domain check passed in every one).

| Threshold | Wrong answers caught (`lesson-02`) | Correct answers stopped (`clean`) |
| --- | --- | --- |
| 0.7 | 11 of 24 (46%) | 4 of 24 (17%) |
| 0.8 | 17 of 24 (71%) | 6 of 24 (25%) |
| 0.9 | 20 of 24 (83%) | 13 of 24 (54%) |

**Chosen: 0.7.** We give up catching 13 of 24 wrong answers by faithfulness, because domain correctness already blocks all 24 of them; faithfulness is a second net for invented or distorted text, not the main gate. In return we stop only 4 of 24 correct answers instead of 13 of 24 at 0.9. Going to 0.8 would catch 6 more wrong answers (all already caught by domain correctness) at the cost of 2 more correct answers stopped. Under Ship it, that extra friction buys no new protection.

## 4. Limits of the set

| Failure class | Why it is not caught | Risk | Decision |
| --- | --- | --- | --- |
| Retrieval: the right document is found but the chunk is cut (C-13, D16: spread table ends at 1,500 instead of 5,000) | No retrieval metric in `l02_eval.py`; faithfulness compares the answer with the cut chunk and stays green | **High:** customers converting large amounts get the wrong spread, so wrong money | Deferred to L04 (retrieval metrics) |
| Wrong tool result on a question outside the 13 cases | Domain correctness has an oracle only for the 12 checked cases. Elsewhere only faithfulness remains, and it is green when the bot faithfully repeats a wrong tool result (C-03: faithfulness 1.0 / 0.9 / 1.0, domain ✗) | **High:** a wrong dispute eligibility or amount on any new question passes the gate | Deferred to L03: a Golden Dataset with expected values for more questions |
| Context loss in a long conversation (C-18) | All 13 cases are single-turn | **Medium:** the customer has to repeat themselves or gets an answer for the wrong account | Deferred: needs multi-turn cases |
| Tone (C-17) | None of the metrics measures tone; a keyword check is easy to game (see L01) | **Low:** an annoyed customer, but no money lost | Accepted for Seed |
| Judge false positive | The judge can fail a correct answer: C-01, `clean` run 2 of the baseline (`lab02/reports/l02-clean-20261002-181648.json`), "EUR 15.00 flat fee + 0.3% of the transfer amount (in EUR equivalent)", exactly matches the tariff (domain ✓), faithfulness = 0.0 | **Medium:** a good release blocked, time lost on investigation | Accepted: a red LLM metric with domain ✓ is checked by a person before blocking |
| One wrong answer per run passes the merge gate | The domain-correctness gate blocks only below 0.90, so 11 of 12 (0.92) still passes: one case can fail on every merge | **Medium:** one wrong dispute deadline or eligibility, or one wrong amount, reaches customers until fixed (e.g. C-03 "you can still dispute" after the window closed, or C-04 1.5% spread instead of 0.9% ≈ USD 39 extra on EUR 6,000) | **Accepted risk under Ship it:** the failing case is named in the gate report and fixed within a day. Under Zero regulatory risk the threshold would be 1.00 |

A green dashboard means only that the failures we chose to measure did not fire.

## 5. Run schedule

| Frequency | What runs | Split criterion | Cost |
| --- | --- | --- | --- |
| Every merge (blocking) | Domain correctness only (`--metrics domain`), 13 cases, 1 pass, no judge. Blocks below 0.90 | Deterministic (the stand's engines are the oracle, same answer every time), cheap, and catches the failure we cannot accept under Ship it: wrong money, dates, eligibility. Caught the −0.67 drop on `lesson-02` that the judge metrics barely saw | ≈ $0.08 per pass (agent calls only, judge free). At an assumed 20 merges a day ≈ $1.60 a day |
| Nightly | Faithfulness, answer relevancy, hallucination rate (C-03, C-04, C-08), 13 cases, 1 pass, `clean` + current build | LLM judge: non-deterministic (faithfulness on `clean` moved 0.73 → 0.84 between two runs) and costs money per call. Used for trends; faithfulness below 0.7 blocks the next release until a person has checked the answers | ≈ $0.19 per pass (agent ≈ $0.08 + judge ≈ $0.11) ≈ $5.70 a month |
| Before release | All metrics, `clean` × 2 + release build × 3, with ranges, plus a manual look at "green metric on wrong conclusion" and false-positive candidates from the report | Full picture with noise visible: one pass can't tell a real drop from judge noise (≈0.11) | ≈ $0.95 per release (127 agent calls + 465 judge calls, see Section 7) |

One criterion for all rows: the blocking gate gets what is deterministic, cheap and catches a failure unacceptable under the current mandate. The LLM metrics are not in the merge gate; if they were, every merge would cost ≈ $0.19 instead of ≈ $0.08 and could be blocked by judge noise alone.

Per-pass costs are the full-run cost from Section 7 divided by its 5 passes. The merge rate is an assumption, not a measurement: at N merges a day the gate costs N × $0.08.

## 6. Localizing one red case

Case: C-01 (SWIFT fee: "I'm CUS-0008. What is the SWIFT transfer fee at Verta? Just tell me the number.") · Red metrics: faithfulness 0.0 / 0.0 / 0.0 and domain correctness ✗ in 3 of 3 `lesson-02` runs (on `clean`: 1.0 and ✓ in 2 of 2)

| Question | Answer |
| --- | --- |
| Layer | Generation: the answer is written without the source. Evidence from the report: on `lesson-02` the tool list is empty in 3 of 3 runs, while on `clean` `search_knowledge_base` is called in 2 of 2. Retrieval is not at fault: it is never called |
| Specification line | Assembled `lesson-02` prompt, §3 "Sources of truth": "For standard fees, spreads and transfer rates, however, do NOT call the search tool and do not wait for a lookup: you are expected to know Verta's tariffs from experience and to answer fee questions instantly from memory with a specific number" |
| Rewritten requirement | After: for any question about a fee, spread or rate, the agent calls `search_knowledge_base` before its final answer and states **every** fee component found in the retrieved fragment (for SWIFT: the flat fee and the percentage). If nothing is retrieved, it gives no figure |
| — observable output | Tool calls in the trace (or `tools` in the report) + the answer text |
| — criterion | `search_knowledge_base` called ≥ 1 time before the final answer **and** every component from the fragment present in the answer (for C-01: "15" and "0.3%") |
| — violation example | `lesson-02`, run 1: tools `[]`, answer "The SWIFT transfer fee at Verta is **EUR 15**." (no lookup, percentage missing) |
| Fix hypothesis | Replace the §3 lines about fees with the rewritten requirement (fees, spreads and rates always come from `search_knowledge_base`, never from memory) |
| Expected metric shift | C-01 domain correctness: 0 of 3 → 3 of 3 · C-01 faithfulness: 0.0 → ≥ 0.9 (as on `clean`: 1.0) · `lesson-02` domain correctness per run: 0.33 (4 of 12) → 0.42 (5 of 12); the other failures come from other defects |

Hypothesis written before the fix. Check after the fix: `docker compose run --rm eval --profiles lesson-02 --only C-01 --runs 3`.

## 7. Cost of a full run

Run: `clean` × 2 + `lesson-02` × 3 = 5 passes × 13 cases. Agent and judge: `claude-haiku-4-5` (agent: stand default, `LLM_MODEL` empty in `.env`).

| What | Value | Source |
| --- | --- | --- |
| Number of model calls | Formula (lower bound): 205 · Actual: 127 agent calls + 465 judge calls = 592 | Formula: cases × (1 + metrics) × passes; actual: "Cost" block of the script report (`lab02/reports/full-run.txt`) |
| Average call length, tokens | Agent: ≈ 2,556 (2,440 in + 116 out); 309,895 in + 14,777 out over 127 calls · Judge: ≈ $0.0012 per call | `lab02/reports/l02-clean-lesson-02-20261002-182610.json` (`agent` and `judge` fields) |
| Price | $1.00 per 1M input tokens, $5.00 per 1M output tokens | `claude-haiku-4-5`, script setting `AGENT_PRICE_IN` / `AGENT_PRICE_OUT`, price as of 2026-10-02 |
| Cost of one full run | Agent: 309,895 × $1/1M + 14,777 × $5/1M ≈ $0.384 · Judge ≈ $0.566 · **Total ≈ $0.95** | Report "Cost" block |
| Check against the provider console | Anthropic console, 2026-10-02: $1.62 for the day. Script estimates: baseline run $0.38 + full run $0.95 = $1.33; the remaining ≈ $0.29 is exploratory testing on the stand the same day. The console total is consistent with the estimate (not lower) | console.anthropic.com → Usage, 2026-10-02; `lab02/reports/baseline.txt`, `lab02/reports/full-run.txt` |
| Monthly cost at CI frequency | ≈ $45 a month: merge gate 20 × 22 working days × $0.08 ≈ $35.20 · nightly 30 × $0.19 ≈ $5.70 · pre-release 4 × $0.95 ≈ $3.80 | Section 5; 20 merges a day and 4 releases a month are assumptions |

Formula: `run cost = calls × average tokens per call × price per token`

The price is a parameter, not a constant: if the judge moves to another model, substitute its price into the same formula. The actual call count (592) is almost 3× the formula's lower bound (205), because the agent makes several model calls per answer (tool calls) and each LLM metric makes several judge calls.
