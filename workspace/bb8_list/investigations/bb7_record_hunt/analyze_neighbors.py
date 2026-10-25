import sys; sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts'); import idle
from collections import Counter, defaultdict

rows = []
with open(r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb7_record_hunt\neighbors_out.tsv', encoding='utf-8') as f:
    hdr = f.readline().rstrip('\n').split('\t')
    for line in f:
        parts = line.rstrip('\n').split('\t')
        if len(parts) == len(hdr):
            rows.append(dict(zip(hdr, parts)))

print(f"Total surviving neighbors in neighbors_out.tsv: {len(rows)}")
by_seed = defaultdict(list)
for r in rows:
    by_seed[r['seed']].append(r)

for sd, srows in by_seed.items():
    print(f"\n==================== SEED: {sd} ({len(srows)} survivors) ====================")
    # Group by signature: (max_n, last_P, r1_check, r2_check, b1_check, b2_check, patE)
    sigs = defaultdict(list)
    for r in srows:
        sig = (int(r['max_n']), r['last_P'], r['r1_check'], r['r2_check'], r['b1_check'], r['b2_check'], r['patE'])
        sigs[sig].append(r)
    for sig, mlist in sorted(sigs.items(), key=lambda x: (-x[0][0], x[0])):
        ex = mlist[0]
        print(f"  count={len(mlist):4d} | max_n={sig[0]:3d} P={sig[1]:6s} | R1:{sig[2]} R2:{sig[3]} | B1:{sig[4]} | B2:{sig[5]} | E:{sig[6]}")
        print(f"             ex (dist={ex['dist']}): {ex['machine']} | first_K: {ex['first_K']} | last_K: {ex['last_K']}")
