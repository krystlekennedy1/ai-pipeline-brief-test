# Can an AI-Written Pipeline Brief Be Trusted?

**A small experiment in testing AI output before anyone acts on it**

By Krystle Kennedy

---

## The short version

Sales leaders want a weekly pipeline brief: which deals are at risk, and what to do about them. AI can write that brief in seconds. The harder question is whether anyone should act on it.

I built a test to find out. I created a synthetic pipeline with 34 planted problems, 17 look-alike decoys, and 5 ambiguous cases. Then I compared two ways of asking Claude for the brief: a one-line vague request and a structured prompt with defined rules.

| | Vague prompt | Structured prompt |
|---|---|---|
| Planted problems found (of 34) | about 31 | **34** |
| Decoys wrongly flagged (of 17) | 11 | **0** |
| Precision | about 74% | **100%** |
| Ambiguous cases handled correctly (of 5) | 2 | **5** |
| Evidence errors | none found | none found |

The vague prompt found most of the problems but drew the line in the wrong places. Its headline said $1.82M of large deals were at risk. Under the stated rules the number is $1.39M. A leader acting on the first figure would be working from a number about 30% too high.

**Takeaway:** AI output becomes trustworthy when the rules are written down, the evidence is shown, and unclear cases go to a person.

---

## Why this matters for AI programs

Most AI pilots stop at "it looked right." Looking right is not a measurement. This project is a small example of the habit I think AI program owners need: define success first, build a test with known answers, score the output, then decide how much to trust it.

---

## How the test works

1. **Synthetic data.** 180 fake opportunities (160 open, 20 closed). No employer or customer data was used.
2. **Planted problems.** I deliberately added issues across six rules (listed below), including 3 deals with two problems each.
3. **Decoys.** I added 17 deals that look like problems but sit just outside a rule, such as a deal idle 29 days when the rule says 30.
4. **Ambiguous cases.** I added 5 cases that a careful analyst would send to a human, such as a next step that says "TBD."
5. **An answer key.** Every planted item has a known correct answer, so scoring is a count, not an opinion.
6. **Two prompts.** Same data, same model, different instructions.

### The six rules

| Rule | Definition |
|---|---|
| Stalled | Proposal or Negotiation stage, 30 or more days since last activity |
| Past due close | Open deal with a close date before today |
| Missing next step | Proposal or Negotiation stage with a blank next step |
| Large deal at risk | Over $200,000, closing within 30 days, 14 or more days idle |
| Possible duplicate | Two open deals with the same account name and amount |
| Date order | Last activity dated before the created date (a data quality problem) |

### The two prompts

- **Vague:** "Find problem deals in this pipeline."
- **Structured:** the six rules above with exact thresholds, a rule that every flag must show the field values behind it, a rule to never invent deals or numbers, a separate "Needs a human look" list for anything borderline, and a fixed one-page format. Full text in `v2/brief_prompt_v2.md`.

---

## Results in more detail

**Where the vague prompt went wrong**
- It flagged a deal that is exactly $200,000 as "over $200,000."
- It flagged a deal idle 13 days when the rule needs 14, and one closing in 31 days when the window is 30.
- It used its own 3-week idle cutoff and swept in two deals idle only 29 days.
- It counted six early-stage deals with blank next steps as problems, though the rule covers only late stages.
- It had no section for ambiguous cases, so unclear items were mixed in with real problems.

**Where it did well**
- It found both exact duplicate pairs and correctly ignored a same-name deal with a different amount.
- It did not call a deal due today "past due."
- It caught lowercase stage names and a next step containing only a space, without being asked.

**What the structured prompt did**
- Found all 34 planted problems, listing both rules for each multi-issue deal.
- Flagged none of the 17 decoys. It even named two near-misses and explained why they fell just outside the rule.
- Put all 5 ambiguous cases under "Needs a human look" instead of guessing.
- Showed its evidence for every flag. I checked 179 values (accounts, owners, amounts, dates, day counts, stages) against the data, and all were correct.

---

## What I learned along the way

- **My first dataset was too easy.** Both prompts scored near-perfect on the first version, so it could not tell them apart. Adding decoys and ambiguity is what made the difference visible.
- **Testing found a bug in my own data.** The vague prompt noticed two deals with last-activity dates before their created dates. That was a flaw in my generator. I fixed it and made date order a deliberate rule.
- **A passing score still needs checking.** I confirmed the answer key with a separate script that recomputes every rule from the raw data (`verify_v2.py`).

---

## Limits of this test

I want to be direct about what this does and does not show.

- **One run per prompt.** A single perfect score could be luck. Repeated runs are needed to show consistency.
- **The rules and the key came from the same author.** The structured prompt's score shows it follows explicit instructions precisely. It does not show it could discover the right rules on its own.
- **The vague prompt was not wrong so much as undefined.** Its choices were reasonable. The problem is that two people (or two weeks) would get different answers.
- **Synthetic data is cleaner than real data.** Real pipelines have messier fields, free-text notes, and politics.
- **One model, one task.** I would not generalize beyond this.

---

## Before using anything like this on real data

- Get approval for the data source and access.
- Keep the AI read-only. It reports and never edits records.
- Show evidence for every flag so a person can verify it.
- Route anything ambiguous to a human before the brief goes out.
- Rerun the test set whenever the prompt or model changes, so quality cannot quietly slip.

---

## Where this could go next

Turn the workflow into a small agent: code applies the exact rules, Claude writes the brief and handles judgment calls, a self-check rejects any brief that disagrees with the code, a person approves ambiguous items, and the answer key becomes an automatic regression test.

---

## Repo contents

```
v1/    First, easier dataset and prompt (kept to show the progression)
v2/    Final dataset, answer key, prompts, generator, and verification script
results/    Saved outputs from each run
```

Key files in `v2/`:
- `synthetic_pipeline_v2.csv`: the 180-deal dataset
- `answer_key_v2.csv`: planted problems, decoys, and ambiguous cases
- `brief_prompt_v2.md`: both prompts and the scoring sheet
- `generate_pipeline_v2.py`: how the data was built
- `verify_v2.py`: recomputes every rule and checks the answer key

All data is synthetic.
