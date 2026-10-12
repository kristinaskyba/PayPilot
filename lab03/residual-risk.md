# Residual risk analysis — Golden dataset L03

Set: `golden.jsonl`, `set_hash` 0cdf2f682dad. Mandate: Ship it (from L02, Quality Bar Proposal).

## 1. Coverage matrix
| Layer | Corpus / RAG | Rule engines | Memory | Tools |
| --- | --- | --- | --- | --- |
| Retrieval | not covered | not covered | not covered | not covered |
| Generation | CMP-004, CMP-006, NEG-C10 | CMP-003, FX-002…FX-011 (with -S pairs), LIM-001, DIS-001, DIS-002-N, DIS-C11, DIS-C12; tone (release): TON-001…TON-005 | not covered | not covered |
| Action | not covered | not covered | not covered | LIM-003, DIS-006, DIS-007 (tool result computed by the engine) |

## 2. What the set does not catch
| What is not covered | What happens if it breaks | Defer or accept | Why we live with it now |
| --- | --- | --- | --- |
| Tone and wording of the answer | The customer gets a cold or off-tone answer; money and rules are not affected. The prompt change ("always begin with an apology") touched only 1 of 29 cases (FX-003-S) | accept | The 5 human-oracle cases (TON-001…TON-005) sit in the release gate; the judge arrives at L09 |
| Document retrieval (C-13, C-14) | The bot returns a wrong figure from the documents, or half an answer, and the set does not see it | defer to L04 | The set has no retrieval-layer cases; L04 will add them |
| Memory in a long conversation (C-18) | The bot loses an amount stated at the start of the chat and the set stays silent | defer to L05 | The set has no multi-turn cases that check memory |

Complaints outside the set: C-02 (customer not logged in, general question, nothing to reproduce), C-15 (mobile app freeze, not the bot), C-20 (review without name, date or answer text). C-16 is covered by the human case TON-003.

## 3. Set size
Cost of one run: calls: 29 `daily` cases × 1 run = 29 · tokens: 144,710 (sum of the `tokens` column in `golden-clean-20261009T174227.json`) · price: claude-haiku-4-5, $1 / 1M input and $5 / 1M output = about $0.17.
The report gives only the total token count, so the split is assumed to be 95.5% input and 4.5% output, as measured in L02 (309,895 : 14,777): 138,100 × $1/1M + 6,600 × $5/1M ≈ $0.138 + $0.033.
Formula from section 7 of the Quality Bar Proposal (L02): `cost = calls × average tokens per call × price per token`
Sensitivity: the prompt change altered the result on 1 case of 29 (FX-003-S); the defective profile lesson-03 altered 15 of 29.
Under the opposite mandate this would change: tone would move into the daily run instead of the release gate, and the "accept" decision for tone would become "defer" until there is a judge (L09).
