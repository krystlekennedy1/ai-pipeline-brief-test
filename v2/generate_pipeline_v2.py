import csv, random, itertools
from datetime import date, timedelta

random.seed(7)
AS_OF = date(2026, 11, 7)
ago = lambda n: AS_OF - timedelta(days=n)
ahead = lambda n: AS_OF + timedelta(days=n)

owners = ["Avery Chen", "Jordan Blake", "Priya Nair", "Marcus Hill", "Sofia Reyes",
          "Devon Park", "Lena Ortiz", "Tariq Aziz"]
prefixes = ["Northwind", "Bluepeak", "Harbor", "Summit", "Cedar", "Ironwood", "Lumen",
            "Pioneer", "Redwood", "Silverline", "Tidewater", "Vantage", "Westbrook",
            "Zenith", "Alder", "Beacon", "Crestview", "Driftwood", "Evergreen", "Foxglove",
            "Granite", "Halcyon", "Juniper", "Keystone", "Larkspur", "Meridian"]
suffixes = ["Logistics", "Health", "Foods", "Systems", "Retail", "Energy", "Media", "Labs"]
accounts = [f"{p} {s}" for p, s in itertools.product(prefixes, suffixes)]
random.shuffle(accounts)

open_stages = ["Prospecting", "Qualification", "Proposal", "Negotiation"]
late_stages = {"Proposal", "Negotiation"}
next_steps = ["Schedule discovery call", "Send pricing proposal", "Security review with IT",
              "Exec sponsor meeting", "Legal redline review", "Product demo for team",
              "Confirm budget approval", "Send order form", "Reference call scheduled",
              "Pilot kickoff planning"]
base_amounts = [8000, 12000, 15000, 18000, 24000, 30000, 42000, 55000, 75000, 90000, 120000]

rows = []
N_OPEN, N_CLOSED = 160, 20
for _ in range(N_OPEN):
    rows.append(dict(
        stage=random.choices(open_stages, weights=[25, 30, 25, 20])[0],
        amount=random.choice(base_amounts),
        created=ago(random.randint(25, 200)),
        last_act=ago(random.randint(0, 12)),
        close=ahead(random.randint(31, 150)),
        next_step=random.choice(next_steps)))
for _ in range(N_CLOSED):
    close = ago(random.randint(10, 90))
    rows.append(dict(
        stage=random.choice(["Closed Won", "Closed Lost"]),
        amount=random.choice(base_amounts),
        created=ago(random.randint(130, 300)),
        last_act=close, close=close, next_step=""))

random.shuffle(rows)
for i, r in enumerate(rows):
    r["opp_id"] = f"OPP-{2001 + i}"
    r["account"] = accounts[i]
    r["owner"] = random.choice(owners)

is_open = lambda r: not r["stage"].startswith("Closed")
open_rows = [r for r in rows if is_open(r)]
late_open = [r for r in open_rows if r["stage"] in late_stages]
early_open = [r for r in open_rows if r["stage"] not in late_stages]
closed_rows = [r for r in rows if not is_open(r)]
for pool in (open_rows, late_open, early_open, closed_rows):
    random.shuffle(pool)

used, key = set(), []

def pick(pool):
    for r in pool:
        if r["opp_id"] not in used:
            used.add(r["opp_id"])
            return r
    raise RuntimeError("pool exhausted")

def add(r, rule, action, note):
    key.append((r["opp_id"], rule, action, note))

# ---------- STALLED ----------
for k in range(6):
    r = pick(late_open)
    r["last_act"] = ago(random.randint(31, 70))
    note = "Late stage, no activity in 31+ days"
    if k == 0:
        r["stage"] = r["stage"].lower()
        note += " (stage is lowercase in the source data)"
    add(r, "STALLED", "FLAG", note)
r = pick(late_open); r["last_act"] = ago(30)
add(r, "STALLED", "FLAG", "Exactly 30 days idle, boundary case that meets the 30 or more rule")
for _ in range(2):
    r = pick(late_open); r["last_act"] = ago(29)
    add(r, "STALLED", "DO_NOT_FLAG", "29 days idle, one day under the threshold")

# ---------- PAST DUE ----------
for _ in range(5):
    r = pick(open_rows); r["close"] = ago(random.randint(3, 45))
    add(r, "PAST_DUE_CLOSE", "FLAG", "Open deal with close date before today")
for _ in range(2):
    r = pick(open_rows); r["close"] = AS_OF
    add(r, "PAST_DUE_CLOSE", "DO_NOT_FLAG", "Close date is today, not past due")

# ---------- MISSING NEXT STEP ----------
for k in range(4):
    r = pick(late_open); r["next_step"] = ""
    note = "Proposal/Negotiation with empty next step"
    if k == 0:
        r["stage"] = r["stage"].lower()
        note += " (stage is lowercase in the source data)"
    add(r, "MISSING_NEXT_STEP", "FLAG", note)
r = pick(late_open); r["next_step"] = " "
add(r, "MISSING_NEXT_STEP", "FLAG", "Next step is only a blank space, which counts as empty")
for _ in range(6):
    r = pick(early_open); r["next_step"] = ""
    add(r, "MISSING_NEXT_STEP", "DO_NOT_FLAG", "Early stage with empty next step, rule only covers Proposal/Negotiation")
for val in ["TBD", "see notes"]:
    r = pick(late_open); r["next_step"] = val
    add(r, "MISSING_NEXT_STEP", "NEEDS_HUMAN_LOOK", f"Next step is a placeholder ('{val}'), not truly empty")

# ---------- LARGE DEAL AT RISK ----------
for _ in range(3):
    r = pick(late_open)
    r["amount"] = random.choice([210000, 260000, 340000])
    r["close"] = ahead(random.randint(5, 28))
    r["last_act"] = ago(random.randint(16, 29))
    add(r, "LARGE_DEAL_AT_RISK", "FLAG", "Over $200K, closes within 30 days, idle 14+ days")
r = pick(late_open); r["amount"] = 220000; r["close"] = ahead(15); r["last_act"] = ago(14)
add(r, "LARGE_DEAL_AT_RISK", "FLAG", "Exactly 14 days idle, boundary case that meets the 14 or more rule")
r = pick(late_open); r["amount"] = 200000; r["close"] = ahead(10); r["last_act"] = ago(20)
add(r, "LARGE_DEAL_AT_RISK", "DO_NOT_FLAG", "Amount is exactly $200,000, not over $200K")
r = pick(late_open); r["amount"] = 230000; r["close"] = ahead(12); r["last_act"] = ago(13)
add(r, "LARGE_DEAL_AT_RISK", "DO_NOT_FLAG", "Only 13 days idle, under the 14 day threshold")
r = pick(late_open); r["amount"] = 250000; r["close"] = ahead(31); r["last_act"] = ago(20)
add(r, "LARGE_DEAL_AT_RISK", "DO_NOT_FLAG", "Closes in 31 days, outside the 30 day window")

# ---------- MULTI-ISSUE DEALS ----------
r = pick(late_open); r["last_act"] = ago(45); r["next_step"] = ""
add(r, "STALLED", "FLAG", "Multi-issue deal: stalled and missing next step")
add(r, "MISSING_NEXT_STEP", "FLAG", "Multi-issue deal: stalled and missing next step")
r = pick(late_open); r["close"] = ago(12); r["last_act"] = ago(38)
add(r, "PAST_DUE_CLOSE", "FLAG", "Multi-issue deal: past due and stalled")
add(r, "STALLED", "FLAG", "Multi-issue deal: past due and stalled")
r = pick(late_open); r["amount"] = 310000; r["close"] = ahead(9); r["last_act"] = ago(33)
add(r, "LARGE_DEAL_AT_RISK", "FLAG", "Multi-issue deal: large at risk and stalled")
add(r, "STALLED", "FLAG", "Multi-issue deal: large at risk and stalled")

# ---------- DATE ORDER (data quality) ----------
for _ in range(3):
    r = pick(early_open)
    r["created"] = ago(random.randint(5, 15))
    r["last_act"] = r["created"] - timedelta(days=random.randint(3, 10))
    add(r, "DATE_ORDER", "FLAG", "Last activity date is earlier than created date")
r = pick(early_open); r["last_act"] = None
add(r, "DATE_ORDER", "NEEDS_HUMAN_LOOK", "last_activity_date is blank, cannot test date order")

# ---------- DUPLICATES ----------
for _ in range(2):
    a, b = pick(open_rows), pick(open_rows)
    b["account"], b["amount"] = a["account"], a["amount"]
    add(a, "POSSIBLE_DUPLICATE", "FLAG", f"Same account and amount as {b['opp_id']}, both open")
    add(b, "POSSIBLE_DUPLICATE", "FLAG", f"Same account and amount as {a['opp_id']}, both open")
a, b = pick(open_rows), pick(open_rows)
b["account"] = a["account"]; b["amount"] = a["amount"] + 6000
add(a, "POSSIBLE_DUPLICATE", "DO_NOT_FLAG", f"Same account as {b['opp_id']} but different amount")
add(b, "POSSIBLE_DUPLICATE", "DO_NOT_FLAG", f"Same account as {a['opp_id']} but different amount")
a, b = pick(open_rows), pick(open_rows)
b["account"] = a["account"] + " Inc"; b["amount"] = a["amount"]
add(a, "POSSIBLE_DUPLICATE", "NEEDS_HUMAN_LOOK", f"Near-duplicate account name with {b['opp_id']}, same amount")
add(b, "POSSIBLE_DUPLICATE", "NEEDS_HUMAN_LOOK", f"Near-duplicate account name with {a['opp_id']}, same amount")
a, c = pick(open_rows), pick(closed_rows)
c["account"], c["amount"], c["stage"] = a["account"], a["amount"], "Closed Won"
add(a, "POSSIBLE_DUPLICATE", "DO_NOT_FLAG", f"Matches closed deal {c['opp_id']}, only open pairs count")
add(c, "POSSIBLE_DUPLICATE", "DO_NOT_FLAG", f"Closed deal, ignore")

# ---------- CLEANUP: planting must not create accidental date-order problems ----------
planted_date_order = {k[0] for k in key if k[1] == "DATE_ORDER"}
for r in rows:
    if r["opp_id"] in planted_date_order or r["last_act"] is None:
        continue
    if r["created"] > r["last_act"]:
        r["created"] = r["last_act"] - timedelta(days=random.randint(5, 40))

# ---------- WRITE ----------
rows.sort(key=lambda r: r["opp_id"])
fmt = lambda d: "" if d is None else d.isoformat()
with open("synthetic_pipeline_v2.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["opp_id", "account", "owner", "stage", "amount", "created_date",
                "close_date", "last_activity_date", "next_step"])
    for r in rows:
        w.writerow([r["opp_id"], r["account"], r["owner"], r["stage"], r["amount"],
                    fmt(r["created"]), fmt(r["close"]), fmt(r["last_act"]), r["next_step"]])

with open("answer_key_v2.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["opp_id", "rule", "expected_action", "note"])
    for k in sorted(key):
        w.writerow(k)

from collections import Counter
print(len(rows), "rows")
print(Counter(k[2] for k in key))
