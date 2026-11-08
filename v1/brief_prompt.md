# Weekly Pipeline Brief Prompt (v1)

Paste this into a new Claude chat, then attach synthetic_pipeline.csv.
Do NOT attach answer_key.csv. That file is only for scoring the result afterward.

---

## Prompt

You are a sales operations analyst preparing a weekly pipeline brief for a first-line sales leader who has about 5 minutes to read it.

Today's date is November 7, 2026. The attached CSV is a pipeline of open and closed opportunities. Ignore any opportunity in a Closed Won or Closed Lost stage.

### Flag these five issue types

1. STALLED: Proposal or Negotiation stage with no activity in 30 or more days.
2. PAST_DUE_CLOSE: open deal with a close date before today.
3. MISSING_NEXT_STEP: Proposal or Negotiation stage with an empty next step.
4. LARGE_DEAL_AT_RISK: amount over $200,000, close date within 30 days, and no activity in 14 or more days.
5. POSSIBLE_DUPLICATE: two open opportunities with the same account and the same amount.

### Rules

- Every flagged deal must include its opp_id and the exact field values that triggered the flag (for example, "last_activity_date 2026-09-20, 48 days ago").
- Calculate days using today's date above. Show the number you calculated.
- Only flag a deal if the data clearly meets the rule. If something is borderline or ambiguous, put it in a separate "Needs a human look" list and say why.
- Never invent opportunities, fields, or metrics that are not in the file.
- Do not give a total or count unless you counted it from the data. State how many deals matched each rule.

### Output format

1. **Headline (2 sentences max):** the single most important thing for the leader this week.
2. **Top 3 actions:** three specific actions, each naming the deals involved by opp_id, account, and owner.
3. **Flagged deals:** a table with columns: opp_id, account, owner, amount, issue type, evidence.
4. **Needs a human look:** borderline items, or "None."
5. **Counts:** number of deals flagged per issue type, plus total open deals reviewed.

Keep the whole brief under one page. Use plain language, not jargon.

---

## Scoring your result (Sunday validation step)

Compare the brief to answer_key.csv and fill in:

| Measure | Count |
|---|---|
| Planted issues Claude caught (true positives) | |
| Planted issues Claude missed (false negatives) | |
| Flags that are not in the key (false positives) | |
| Flags with wrong evidence (wrong days, amounts, dates) | |
| Invented deals or fields | |

Quick formulas:
- Recall = caught / 22
- Precision = caught / (caught + false positives)

Note: the key has 22 entries across 22 different deals. The duplicate pair counts as two entries, one for each deal in the pair.
Run the prompt 3 times and note whether the results change. Consistency is part of the story.
