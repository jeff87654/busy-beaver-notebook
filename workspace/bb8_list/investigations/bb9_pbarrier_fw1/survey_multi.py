import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from pathlib import Path

p1 = Path(r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits\out.tsv')
p2 = Path(r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_triage7\out.tsv')

def load_tsv(p):
    rows = []
    for line in p.read_text().splitlines()[1:]:
        if not line.strip() or line.startswith('#'):
            continue
        parts = line.split('\t')
        if len(parts) >= 7:
            rows.append(parts)
    return rows

r1 = load_tsv(p1)
r2 = load_tsv(p2)
print(f"dl3_hits: {len(r1)} rows, dl3_triage7: {len(r2)} rows")

by_m = {}
for r in r1:
    by_m[r[0]] = ('hits', r)
for r in r2:
    if r[0] not in by_m:
        by_m[r[0]] = ('triage7_new', r)
    else:
        by_m[r[0]] = ('both', r)

from collections import Counter
c = Counter((src, r[3]) for src, r in by_m.values())
for k, v in sorted(c.items()):
    print(f"  {k}: {v}")

print("\n--- ALL MULTI and MULTI? machines ---")
multi_list = []
for m, (src, r) in sorted(by_m.items()):
    if r[3] in ('MULTI', 'MULTI?'):
        multi_list.append((src, r))

print(f"Total unique MULTI/MULTI?: {len(multi_list)}")
# Group by (template, params)
groups = {}
for src, r in multi_list:
    key = (r[3], r[4], r[6])
    groups.setdefault(key, []).append((src, r[0], r[5]))

for key, items in sorted(groups.items()):
    print(f"\nGroup {key} ({len(items)} machines):")
    for src, m, w1 in items[:5]:
        print(f"  [{src}] {m}  w1={w1[:80]}")
    if len(items) > 5:
        print(f"  ... and {len(items)-5} more")
