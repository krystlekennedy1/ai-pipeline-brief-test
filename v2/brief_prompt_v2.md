# Weekly Pipeline Brief: v2 Test Kit

Files: synthetic_pipeline_v2.csv (attach to the chat), answer_key_v2.csv (do NOT attach, scoring only).

## How to run the experiment

Use a fresh chat for every run so nothing carries over.

| Run | Prompt | Times |
|---|---|---|
| A | Baseline (below) | 3 |
| B | Structured v2 (below) | 3 |

Save each full output as text before you score it.

---

## Prompt A: Baseline

Review this sales pipeline and tell me which deals are problems and what I should do about them.

---

## Prompt B: Structured v2

You are a sales operations analyst preparing a weekly pipeline brief for a first-line sales leader who has about 5 minutes to read it.

Today's date is November 7, 2026. The attached CSV is a pipeline of open and closed opportunities. Ignore any opportunity whose stage starts with "Closed". Treat stage names as the same regardless of capital letters.

### Flag these six issue types

1. STALLED: Proposal or Negotiation stage with 30 or more days since the last activity date.
2. PAST_DUE_CLOSE: open deal with a close date earlier than today. A close date of today is not past due.
3. MISSING_NEXT_STEP: Proposal or Negotiation stage with an empty or blank next step. Early stages do not count.
4. LARGE_DEAL_AT_RISK: amount strictly over $200,000, close date from today through 30 days from today, and 14 or more days since the last activity date.
5. POSSIBLE_DUPLICATE: two or more open opportunities with exactly the same account name and the same amount. Closed deals do not count.
6. DATE_ORDER: last activity date is earlier than the created date. This is a data quality problem.

### Rules

- A deal can hit more than one rule. List each rule it hits as its own row.
- Every flagged deal must include its opp_id and the exact field values that triggered the flag (for example, "last_activity_date 2026-09-20, 48 days ago").
- Calculate days using today's date above. Show the number you calculated.
- Only flag a deal if the data clearly meets the rule exactly as written. If something is borderline, ambiguous, blank, or looks like a near match (for example a placeholder next step, a missing date, or a similar but not identical account name), put it in "Needs a human look" and say why. Do not flag it.
- Never invent opportunities, fields, or metrics that are not in the file.
- Do not give a total or count unless you counted it from the data. State how many deals matched each rule.

### Output format

1. **Headline (2 sentences max):** the single most important thing for the leader this week.
2. **Top 3 actions:** three specific actions, each naming the deals involved by opp_id, account, and owner.
3. **Flagged deals:** a table with columns: opp_id, account, owner, amount, issue type, evidence.
4. **Needs a human look:** borderline items with the reason, or "None."
5. **Counts:** number of flagged rows per issue type, plus total open deals reviewed.

Keep the whole brief under one page. Use plain language, not jargon.

---

## Scoring (use answer_key_v2.csv)

The key has three kinds of rows:
- FLAG (34 rows across 31 deals): the brief should flag these.
- DO_NOT_FLAG (17 rows): decoys that look like problems but do not meet the rule exactly. Flagging one is a "trap hit."
- NEEDS_HUMAN_LOOK (5 rows): ambiguous items. Best outcome is listing them under "Needs a human look."

Fill in one column per run:

| Measure | A1 | A2 | A3 | B1 | B2 | B3 |
|---|---|---|---|---|---|---|
| FLAG rows caught (of 34) | | | | | | |
| FLAG rows missed | | | | | | |
| Trap hits (decoys flagged) | | | | | | |
| Flags not in the key at all | | | | | | |
| Human-look items placed correctly (of 5) | | | | | | |
| Wrong evidence (days, dates, amounts) | | | | | | |
| Invented deals or fields | | | | | | |

Formulas:
- Recall = caught / 34
- Precision = caught / (caught + trap hits + flags not in key)

Things to compare across the 3 runs of each prompt:
- Do the same deals get flagged every time?
- Which boundary cases (exactly 30 days, exactly 14 days, exactly $200,000) flip between runs?
- Does the 3-issue-in-one-deal pattern get both rules listed?

Note: Prompt A will not know about the DATE_ORDER rule or the exact thresholds. That is expected. The point is to measure how much the structure of Prompt B changes accuracy, consistency, and evidence quality.
