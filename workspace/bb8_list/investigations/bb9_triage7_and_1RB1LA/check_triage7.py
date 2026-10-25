import sys, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

HERE = os.path.dirname(os.path.abspath(__file__))
hits_path = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\hits_triage7.tsv'
dl3_tr_out = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_triage7\out.tsv'
dl3_hits_out = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits\out.tsv'

def read_tsv_machines(path):
    rows = {}
    if not os.path.exists(path):
        return rows
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.rstrip('\r\n')
            if not line or line.startswith('machine\t') or line.startswith('#'):
                continue
            parts = line.split('\t')
            tm = parts[0].strip()
            if len(tm) == 48 and '_' in tm:
                rows[tm] = parts
    return rows

hits_rows = {}
with open(hits_path, 'r', encoding='utf-8', errors='replace') as f:
    for line in f:
        line = line.rstrip('\r\n')
        if not line: continue
        for p in line.split('\t'):
            p = p.strip()
            if len(p) == 48 and p.count('_') == 6:
                hits_rows[p] = line
                break

dl3_tr = read_tsv_machines(dl3_tr_out)
dl3_1pct = read_tsv_machines(dl3_hits_out)

missing = sorted(set(hits_rows.keys()) - set(dl3_tr.keys()))
print(f"hits_triage7 unique TMs: {len(hits_rows)}")
print(f"dl3_triage7/out.tsv unique TMs: {len(dl3_tr)}")
print(f"dl3_hits/out.tsv (1% sample) unique TMs: {len(dl3_1pct)}")
print(f"Missing from dl3_triage7/out.tsv: {len(missing)}")

new_m_file = os.path.join(HERE, 'new_machines.txt')
with open(new_m_file, 'w', encoding='utf-8') as f:
    for m in missing:
        f.write(m + '\n')

# Inspect grades in dl3_tr that are NOT in dl3_1pct
by_grade = {}
for m, parts in dl3_tr.items():
    grade = parts[3] if len(parts) > 3 else '?'
    in_1pct = m in dl3_1pct
    by_grade.setdefault((grade, in_1pct), []).append((m, parts))

print("\nBreakdown of dl3_triage7/out.tsv by (grade, in_1pct):")
for k in sorted(by_grade.keys()):
    print(f"  {k}: {len(by_grade[k])}")

print("\n--- NEW (not in 1% sample) interesting grades in dl3_triage7/out.tsv ---")
for (grade, in_1pct), items in sorted(by_grade.items()):
    if in_1pct: continue
    if grade in ('R4-SOME', 'REBUILD', 'HALT-SOME', 'CHAMPION', 'HALT?'):
        print(f"\n=== Grade: {grade} ({len(items)} machines) ===")
        for m, parts in items:
            print("  " + "\t".join(parts))
