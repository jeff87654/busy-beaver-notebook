import json, os

VERDICTS = r"C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\final_all_verdicts.tsv"
FAMILIES = r"C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\final_all_families.tsv"
POOL_JSON = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_m8sweep\pool.json"

with open(POOL_JSON) as f:
    m8_pool = json.load(f)["pool"]

verdicts = []
with open(VERDICTS) as f:
    hdr = f.readline().strip().split("\t")
    for line in f:
        if not line.strip(): continue
        verdicts.append(line.strip().split("\t"))

not_in_pool = []
for r in verdicts:
    m = r[0]
    v = r[3]
    if "NEVER-HALTS" in v and m not in m8_pool:
        not_in_pool.append(r)

print(f"NEVER-HALTS rows in reb7 NOT in m8sweep pool.json: {len(not_in_pool)}")
by_stage = {}
for r in not_in_pool:
    st = f"{r[4]} | {r[3]} | {r[5][:40]}"
    by_stage.setdefault(st, []).append(r)

for st, rows in sorted(by_stage.items()):
    print(f"\n--- {st} ({len(rows)} rows) ---")
    for r in rows[:15]:
        print("  ", r[0], "|", r[5][:60], "|", r[6])
    if len(rows) > 15:
        print(f"  ... ({len(rows)-15} more)")
