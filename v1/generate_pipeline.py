import csv, random, itertools
from datetime import date, timedelta

random.seed(42)
AS_OF = date(2026, 11, 7)

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

rows = []
n_open, n_closed = 135, 15
for i in range(n_open):
    stage = random.choices(open_stages, weights=[25, 30, 25, 20])[0]
    amount = random.choice([8000, 12000, 15000, 18000, 24000, 30000, 42000, 55000, 75000, 90000, 120000])
    created = AS_OF - timedelta(days=random.randint(20, 150))
    last_act = AS_OF - timedelta(days=random.randint(0, 12))
    close = AS_OF + timedelta(days=random.randint(10, 120))
    rows.append(dict(stage=stage, amount=amount, created=created, last_act=last_act,
                     close=close, next_step=random.choice(next_steps)))
for i in range(n_closed):
    stage = random.choice(["Closed Won", "Closed Lost"])
    amount = random.choice([12000, 24000, 42000, 75000])
    created = AS_OF - timedelta(days=random.randint(120, 260))
    close = AS_OF - timedelta(days=random.randint(10, 90))
    rows.append(dict(stage=stage, amount=amount, created=created,
                     last_act=close, close=close, next_step=""))

random.shuffle(rows)
for idx, r in enumerate(rows):
    r["opp_id"] = f"OPP-{1001 + idx}"
    r["account"] = accounts[idx]
    r["owner"] = random.choice(owners)

open_rows = [r for r in rows if not r["stage"].startswith("Closed")]
late_open = [r for r in open_rows if r["stage"] in late_stages]
random.shuffle(open_rows)
random.shuffle(late_open)
used = set()
key = []

def pick(pool):
    for r in pool:
        if r["opp_id"] not in used:
            used.add(r["opp_id"])
            return r

# 1. Stalled: late stage, no activity 35-60 days
for _ in range(6):
    r = pick(late_open)
    r["last_act"] = AS_OF - timedelta(days=random.randint(35, 60))
    key.append((r["opp_id"], "STALLED", "Late stage (Proposal/Negotiation) with no activity in 30+ days"))

# 2. Past-due close dates on open deals
for _ in range(5):
    r = pick(open_rows)
    r["close"] = AS_OF - timedelta(days=random.randint(5, 40))
    key.append((r["opp_id"], "PAST_DUE_CLOSE", "Open deal with close date already in the past"))

# 3. Missing next step in late stage
for _ in range(6):
    r = pick(late_open)
    r["next_step"] = ""
    key.append((r["opp_id"], "MISSING_NEXT_STEP", "Late stage deal with no next step recorded"))

# 4. Large deal closing soon with no recent activity
for _ in range(3):
    r = pick(late_open)
    r["amount"] = random.choice([210000, 260000, 340000])
    r["close"] = AS_OF + timedelta(days=random.randint(7, 24))
    r["last_act"] = AS_OF - timedelta(days=random.randint(16, 24))
    key.append((r["opp_id"], "LARGE_DEAL_AT_RISK", "Amount over $200K, closing within 30 days, no activity in 14+ days"))

# 5. Duplicate account entries (possible duplicate opportunity)
dup_src = pick(open_rows)
dup = pick(open_rows)
dup["account"] = dup_src["account"]
dup["amount"] = dup_src["amount"]
key.append((dup["opp_id"], "POSSIBLE_DUPLICATE", f"Same account and amount as {dup_src['opp_id']}"))
key.append((dup_src["opp_id"], "POSSIBLE_DUPLICATE", f"Same account and amount as {dup['opp_id']}"))

rows.sort(key=lambda r: r["opp_id"])
fields = ["opp_id", "account", "owner", "stage", "amount", "created_date",
          "close_date", "last_activity_date", "next_step"]
with open("synthetic_pipeline.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(fields)
    for r in rows:
        w.writerow([r["opp_id"], r["account"], r["owner"], r["stage"], r["amount"],
                    r["created"], r["close"], r["last_act"], r["next_step"]])

with open("answer_key.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["opp_id", "planted_issue", "why_it_should_be_flagged"])
    for k in sorted(key):
        w.writerow(k)

print(len(rows), "rows;", len(key), "key entries")
