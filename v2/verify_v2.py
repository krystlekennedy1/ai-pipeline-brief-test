"""Recompute every pipeline rule from the CSV alone and compare to the answer key.

Usage: python3 verify_v2.py
Expects synthetic_pipeline_v2.csv and answer_key_v2.csv in the same folder.
Prints any mismatch between the rules and the key. A clean run means the key is correct.
"""
import csv
from datetime import date
from collections import defaultdict

AS_OF = date(2026, 11, 7)
parse = lambda s: date.fromisoformat(s) if s else None

rows = list(csv.DictReader(open("synthetic_pipeline_v2.csv")))
key = list(csv.DictReader(open("answer_key_v2.csv")))

open_rows = [r for r in rows if not r["stage"].strip().lower().startswith("closed")]
is_late = lambda r: r["stage"].strip().lower() in ("proposal", "negotiation")

found = set()
by_account_amount = defaultdict(list)
for r in open_rows:
    by_account_amount[(r["account"], r["amount"])].append(r["opp_id"])

for r in open_rows:
    last, created, close = parse(r["last_activity_date"]), parse(r["created_date"]), parse(r["close_date"])
    idle = (AS_OF - last).days if last else None
    if is_late(r) and idle is not None and idle >= 30:
        found.add((r["opp_id"], "STALLED"))
    if close < AS_OF:
        found.add((r["opp_id"], "PAST_DUE_CLOSE"))
    if is_late(r) and not r["next_step"].strip():
        found.add((r["opp_id"], "MISSING_NEXT_STEP"))
    if int(r["amount"]) > 200000 and 0 <= (close - AS_OF).days <= 30 and idle is not None and idle >= 14:
        found.add((r["opp_id"], "LARGE_DEAL_AT_RISK"))
    if last and last < created:
        found.add((r["opp_id"], "DATE_ORDER"))

for ids in by_account_amount.values():
    if len(ids) > 1:
        for opp_id in ids:
            found.add((opp_id, "POSSIBLE_DUPLICATE"))

expected = {(k["opp_id"], k["rule"]) for k in key if k["expected_action"] == "FLAG"}
decoys = {(k["opp_id"], k["rule"]) for k in key if k["expected_action"] == "DO_NOT_FLAG"}

print(f"Rules found {len(found)} flags; key expects {len(expected)}.")
print("In key but not found:", sorted(expected - found) or "none")
print("Found but not in key:", sorted(found - expected) or "none")
print("Decoys that trigger a rule:", sorted(decoys & found) or "none")
