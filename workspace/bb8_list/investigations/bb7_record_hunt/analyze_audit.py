import sys; sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts'); import idle
from collections import Counter

rows = []
with open(r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb7_record_hunt\audit_out.tsv', encoding='utf-8') as f:
    hdr = f.readline().rstrip('\n').split('\t')
    for line in f:
        parts = line.rstrip('\n').split('\t')
        rows.append(dict(zip(hdr, parts)))

print(f"Total audited rows: {len(rows)}")
print("By (grade, patL):", Counter((r['grade'], r['patL']) for r in rows).most_common(30))

print("\n=== ALL ROWS WHERE patL != 'KKKKKKKKKKKK' (excluding already-ranked CHAMPION/R4-SOME) ===")
non_k = [r for r in rows if r['patL'] != 'KKKKKKKKKKKK' and r['grade'] not in ('CHAMPION', 'R4-SOME')]
print(f"Count: {len(non_k)}")
for r in non_k:
    print(f"{r['grade']:11s} {r['machine']} | max_n={r['max_n']:3s} | tmpl={r['tmpl']:38s} | {r['refit_r3']:35s} | patS={r['patS']} patL={r['patL']} | {r['last_K']}")

print("\n=== ALL HALT-SOME ROWS (even if patL == KKKKKKKKKKKK) ===")
hs = [r for r in rows if r['grade'] == 'HALT-SOME']
print(f"Count: {len(hs)}")
for r in hs:
    print(f"{r['machine']} | max_n={r['max_n']:3s} | tmpl={r['tmpl']:38s} | {r['params'][:45]:45s} | {r['refit_r3']:32s} | patS={r['patS']} patL={r['patL']} | {r['last_K']}")

print("\n=== ALL ROWS WITH max_n >= 15 (any grade) ===")
big_n = [r for r in rows if int(r['max_n']) >= 15]
print(f"Count: {len(big_n)}")
for r in sorted(big_n, key=lambda x: -int(x['max_n'])):
    print(f"{r['grade']:11s} {r['machine']} | max_n={r['max_n']:3s} | tmpl={r['tmpl']:38s} | {r['refit_r3']:32s} | patS={r['patS']} patL={r['patL']} | {r['last_K']}")
