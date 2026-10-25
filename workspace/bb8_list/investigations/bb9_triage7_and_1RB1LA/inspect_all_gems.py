import sys, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

HERE = os.path.dirname(os.path.abspath(__file__))
dl3_tr_out = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_triage7\out.tsv'
dl3_hits_out = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits\out.tsv'
new_dl3_out = os.path.join(HERE, 'new_dl3_out.tsv')

def read_tsv(path):
    rows = {}
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.rstrip('\r\n')
            if not line or line.startswith('machine\t') or line.startswith('#'):
                continue
            parts = line.split('\t')
            rows[parts[0]] = parts
    return rows

tr = read_tsv(dl3_tr_out)
new_tr = read_tsv(new_dl3_out)
old_1pct = read_tsv(dl3_hits_out)

combined = dict(tr)
combined.update(new_tr)

print(f"Total combined dl3 rows for hits_triage7: {len(combined)}")
by_grade = {}
for m, parts in combined.items():
    g = parts[3]
    in_1pct = m in old_1pct
    by_grade.setdefault((g, in_1pct), []).append(parts)

for k in sorted(by_grade.keys()):
    print(f"  {k}: {len(by_grade[k])}")

for (g, in_1pct), items in sorted(by_grade.items()):
    if in_1pct: continue
    if g in ('W1-HALTER=0', 'W1-LOOPER', 'MULTI', 'R4-SOME', 'REBUILD', 'HALT-SOME', 'CHAMPION'):
        print(f"\n=== Combined NEW Grade: {g} ({len(items)}) ===")
        for parts in items:
            print("  " + "\t".join(parts))
