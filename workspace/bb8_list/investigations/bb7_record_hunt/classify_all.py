import sys; sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts'); import idle
from collections import Counter

rows = []
with open(r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb7_record_hunt\audit_out.tsv', encoding='utf-8') as f:
    hdr = f.readline().rstrip('\n').split('\t')
    for line in f:
        parts = line.rstrip('\n').split('\t')
        rows.append(dict(zip(hdr, parts)))

print(f"Total audited rows: {len(rows)}")
print("By (grade, patL):")
for (g, pl), cnt in Counter((r['grade'], r['patL']) for r in rows).most_common():
    print(f"  {g:12s} {pl:14s} : {cnt}")

print("\n=== 1. ALL ROWS WITH 'H' IN patL (excluding CHAMPION/R4-SOME) ===")
for r in rows:
    if 'H' in r['patL'] and r['grade'] not in ('CHAMPION', 'R4-SOME'):
        print(f"{r['grade']:10s} {r['machine']} | max_n={r['max_n']:3s} | {r['tmpl']:35s} | {r['strip_P']:25s} | {r['refit_r3']:32s} | patS={r['patS']} patL={r['patL']} | {r['last_K']} | {r['exh_detail'][:100]}")

print("\n=== 2. ALL ROWS WITH patL != 'KKKKKKKKKKKK' AND NO 'H' IN patL (excluding CHAMPION/R4-SOME) ===")
for r in rows:
    if r['patL'] != 'KKKKKKKKKKKK' and 'H' not in r['patL'] and r['grade'] not in ('CHAMPION', 'R4-SOME'):
        print(f"{r['grade']:10s} {r['machine']} | max_n={r['max_n']:3s} | {r['tmpl']:35s} | {r['strip_P']:25s} | {r['refit_r3']:32s} | patS={r['patS']} patL={r['patL']} | {r['last_K']} | {r['exh_detail'][:100]}")

print("\n=== 3. ALL ROWS WITH 'H' IN patS BUT patL == 'KKKKKKKKKKKK' (excluding CHAMPION/R4-SOME) ===")
for r in rows:
    if 'H' in r['patS'] and r['patL'] == 'KKKKKKKKKKKK' and r['grade'] not in ('CHAMPION', 'R4-SOME'):
        print(f"{r['grade']:10s} {r['machine']} | max_n={r['max_n']:3s} | {r['tmpl']:35s} | {r['strip_P']:25s} | {r['refit_r3']:32s} | patS={r['patS']} patL={r['patL']} | {r['last_K']}")

print("\n=== 4. ALL ROWS WHERE refit_r3 == 'FAIL' (excluding CHAMPION/R4-SOME) ===")
for r in rows:
    if r['refit_r3'] == 'FAIL' and r['grade'] not in ('CHAMPION', 'R4-SOME'):
        print(f"{r['grade']:10s} {r['machine']} | max_n={r['max_n']:3s} | {r['tmpl']:35s} | {r['params'][:45]:45s} | patS={r['patS']} patL={r['patL']} | {r['last_K']}")
