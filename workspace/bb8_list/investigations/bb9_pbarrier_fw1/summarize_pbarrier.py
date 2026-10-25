import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from pathlib import Path

p = Path(r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_pbarrier_fw1\pbarrier_scan_out.tsv')
text = p.read_bytes().decode('utf-16le')
p.write_text(text, encoding='utf-8')

lines = [l.strip().split('\t') for l in text.splitlines() if l.strip()]
header = lines[0]
rows = lines[1:]
print(f"Total scanned: {len(rows)}")

# Filter for machines with E_only != '-' or interesting E_map
print("\n=== MACHINES WITH E-ONLY SLOTS (E_only != '-') ===")
for r in rows:
    if len(r) < 13: continue
    m, grade, tmpl, P_true, B0, btrace, emap, mD, mB, mE, e_only, b_only, undef = r[:13]
    if e_only != '-':
        print(f"{m} [{grade}] P_true={P_true} B0={B0} E_only={e_only} B_only={b_only} undef={undef}")
        print(f"  tmpl={tmpl}")
        print(f"  blank={btrace[:120]}")
        print(f"  emap={emap}")

print("\n=== ALL P_true != '-' MACHINES WHERE E_map REBUILDS GROWING LISTS ===")
for r in rows:
    if len(r) < 13: continue
    m, grade, tmpl, P_true, B0, btrace, emap, mD, mB, mE, e_only, b_only, undef = r[:13]
    if P_true != '-' and '(L' in emap:
        print(f"{m} [{grade}] P_true={P_true} B0={B0} E_only={e_only} B_only={b_only} undef={undef} | emap={emap[:90]} | blank={btrace[:80]}")
