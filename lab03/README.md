# L03 · Automated Eval Suite — PayPilot

## Запуск
Put `golden.jsonl` into `l03/sets/` and `generate_golden.py` into `l03/` (the course kit folder, next to `paypilot-stand`), then run:

    docker compose run --rm eval --set golden --profile clean

`set_hash`: 0cdf2f682dad

## Скарги
| Скарга | Кейс | Клієнт / операція | Оракул |
| --- | --- | --- | --- |
| C-11 | DIS-C11 | CUS-0009 / TX-0902 (fraud, 120 days) | engine |
| C-12 | DIS-C12 | CUS-0002 / TX-0201 (duplicate charge, 60 days) | engine |
| C-10 | NEG-C10, TON-004 | CUS-0006 / TX-0601 (compliance hold) | corpus (regulatory.md), human |
| C-17 | TON-001 | CUS-0004 (angry, charged twice) | human |
| C-03 | TON-002 | CUS-0004 / TX-0402 | human |
| C-16 | TON-003 | CUS-0001 | human |
| C-19 | TON-005 | CUS-0001 | human |

## Генератор
Додані межі: free FX allowance, all-or-nothing rule. Each boundary is a pair: the amount that uses the allowance up exactly, and +1 EUR.
- FX-006 / FX-007: CUS-0007 (tier 2, 0 used): 1000 / 1001 EUR
- FX-008 / FX-009: CUS-0002 (tier 2, 800 used): 200 / 201 EUR
- FX-010 / FX-011: CUS-0001 (tier 1, 120 used): 380 / 381 EUR

Критерій відбору: the 14 kit cases stay as the base. From the generator I took only the new boundary rows and the new complaint rows (DIS-C11, DIS-C12); rows that duplicate kit cases were left out. Every boundary has a pair: an amount case and a spread case ("-S").

Знахідки: one euro more means less money. 1000 EUR gives 1086.96 USD but 1001 EUR gives 1078.25 USD (-8.71), 200 / 201 EUR for CUS-0002 give 217.39 / 216.51 USD, and 380 / 381 EUR for CUS-0001 give 413.04 / 407.92 USD. That is the all-or-nothing rule: past the allowance, the spread applies to the whole amount.
Also (C-03): TX-0402 is 63 days old on 15 Sep, outside the 60-day window, but TX-0401 (57 days) is still inside, so the dispute may have been filed on the wrong charge.

## Прогони
| Прогін | Профіль | Результат | Звіт |
| --- | --- | --- | --- |
| Baseline | `clean` | 29/29 | `reports/golden-clean-20261009T174227.json` |
| Дефектна система | `lesson-03` | 14/29 | `reports/golden-lesson-03-20261009T174405.json` |
| Зміна промпту | `clean` + рядок | 28/29 | `reports/golden-clean-20261009T175055.json` |

All three reports have the same `set_hash` 0cdf2f682dad, so they are comparable.

Line in the prompt: `Never use the % sign. Always write the word "percent" instead.`

Prediction before the run (round 2, written after the mentor's feedback and before the third run):
I expect exactly 4 of the 29 daily cases to fail: FX-003-S, FX-007-S and FX-009-S (each looks for the text "0.9%" in the answer) and FX-011-S (looks for "1.5%"). The bot will write "percent" instead of "%", so the text check will not find the string, even though the answer is still correct. The other 25 should pass: the 13 cases that read the tool result (FX-002 to FX-011, LIM-003, DIS-006, DIS-007) do not depend on wording, and the "must not say" checks (FX-006-S, FX-008-S, FX-010-S) can only get easier to pass without "%". Risk: the model may not follow the line in every answer, so I may see fewer than 4 failures.

Round 1 prediction (superseded after the mentor's feedback: it named no case ids): "I expect a few of the 29 daily cases (1-5) to fail, but I can't say which ones." The prompt line then was: `Always begin your answer with a short apology.`

Коміт із прогнозом: 9bfcfed ("docs: lab 03 prediction before prompt-change run", committed before the third run)

Що впало (prompt change): FX-003-S (L3, contains) - '0.9%' was not in the answer. Control check: the same case with the original prompt, run alone, passes (1/1). With one run each, this points to the apology line as the cause but does not prove it.

Розбіжність із прогнозом: I predicted 1-5 failures; I got 1, at the low end of my range. My claim that numeric (L2) and "must not say" (L4) checks would still pass held. I did not predict that a wording check (L3) would be the one to fail: the apology line changed how the answer is phrased, so the exact text the check looks for disappeared while the number stayed correct. The set sees a prompt change only through this one check and cannot see tone itself (the 5 tone cases are in the release gate).

Дефекти (lesson-03 run, 15 of 29 cases failed):
- D19 (wrong dispute window): caught by DIS-002-N, DIS-006
- D20 (wrong tier spread): caught by FX-002, FX-003, FX-005 (also FX-004, FX-003-S)
- D21 (spread on part of the amount): caught by FX-007, FX-007-S, FX-009, FX-009-S, FX-011, FX-011-S
- D22 (daily limit given as monthly): caught by LIM-003
- D26 (compliance hold ignored): caught by DIS-007
Missed: none of the five.
