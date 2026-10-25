import os, glob, collections

NONLIST = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist'
TRIAGE = os.path.join(NONLIST, 'rcands_triage')
os.makedirs(TRIAGE, exist_ok=True)

# 1. Copy clean snapshot of all complete lines currently in rcands.tsv -> rcands_snap.tsv
rcands_src = os.path.join(NONLIST, 'rcands.tsv')
rcands_snap = os.path.join(TRIAGE, 'rcands_snap.tsv')

snap_lines = []
with open(rcands_src, 'r', encoding='utf-8', errors='replace') as f:
    for line in f:
        if line.endswith('\n'):
            snap_lines.append(line)

with open(rcands_snap, 'w', encoding='utf-8') as f:
    f.writelines(snap_lines)

print(f"rcands_snap.tsv written: {len(snap_lines)} complete lines ({os.path.getsize(rcands_snap)} bytes)")

# Parse rcands_snap.tsv
snap_rows = []
for l in snap_lines:
    if l.startswith(('class', '#')):
        continue
    parts = l.rstrip('\n').split('\t')
    if len(parts) >= 13:
        snap_rows.append(parts)

snap_cls = collections.Counter(r[0] for r in snap_rows)
snap_fams = len(snap_rows)
snap_machs = sum(int(r[2]) for r in snap_rows)
print(f"In rcands_snap.tsv: {snap_fams} family rows, representing {snap_machs} FAST machines. By class: {dict(snap_cls)}")

# 2. Check completed rpil/r*.tsv and rfull/r*.tsv
def is_done(p):
    if not os.path.exists(p): return False
    with open(p, 'rb') as f:
        f.seek(0, 2)
        n = f.tell()
        f.seek(max(0, n - 300))
        return b'#summary' in f.read()

rpil_files = [p for p in sorted(glob.glob(os.path.join(NONLIST, 'rpil', 'r*.tsv'))) if is_done(p)]
rfull_files = [p for p in sorted(glob.glob(os.path.join(NONLIST, 'rfull', 'r*.tsv'))) if is_done(p)]
print(f"Completed rpil files: {len(rpil_files)} ({os.path.basename(rpil_files[0])} .. {os.path.basename(rpil_files[-1])})")
print(f"Completed rfull files: {len(rfull_files)} ({os.path.basename(rfull_files[0])} .. {os.path.basename(rfull_files[-1])})")

# 3. Run collect.py logic across ALL completed rfull files, and also check how many rfull files made rcands.tsv
def fl(x):
    try: return float(x)
    except ValueError: return 0.0

rows_all = []
nmach_all = 0
for idx, p in enumerate(rfull_files):
    for l in open(p, 'r', encoding='utf-8', errors='replace'):
        if l.startswith(('#', 'machine')): continue
        f = l.rstrip('\n').split('\t')
        if len(f) < 18: continue
        nmach_all += 1
        rows_all.append((os.path.basename(p), f))

fast_all = [(fn, f) for fn, f in rows_all if fl(f[3]) >= 9.8 or (fl(f[11]) >= 9.8 and f[11] != '99.00')]
halts_all = [(fn, f) for fn, f in rows_all if f[2] == 'HALT' or f[15] == 'HALT']
fam_all = collections.OrderedDict()
for fn, f in fast_all:
    key = (f[3], f[4], f[6], f[9], f[16], f[11])
    fam_all.setdefault(key, []).append((fn, f))

c1_all = [(v[0][1], len(v), v[0][0]) for v in fam_all.values() if int(v[0][1][16]) > 0]
c2_all = [(v[0][1], len(v), v[0][0]) for v in fam_all.values() if int(v[0][1][16]) == 0 and int(v[0][1][6]) >= 10]
c3_other_fast = [(v[0][1], len(v), v[0][0]) for v in fam_all.values() if int(v[0][1][16]) == 0 and int(v[0][1][6]) < 10]
c1_all.sort(key=lambda x: (-int(x[0][6]), -int(x[0][16])))
c2_all.sort(key=lambda x: -int(x[0][6]))

print(f"\nAcross ALL {len(rfull_files)} completed rfull chunks:")
print(f"  Total Stage-B rows (gate passers P2>=8|nsr>=2): {nmach_all}")
print(f"  Total FAST rows (nat_lg>=9.8 or k2_lg>=9.8): {len(fast_all)} ({len(fam_all)} unique families)")
print(f"  FR > 0 families (class FR): {len(c1_all)} families ({sum(n for _, n, _ in c1_all)} machines)")
print(f"  FR == 0 & SRs >= 10 families (class SR): {len(c2_all)} families ({sum(n for _, n, _ in c2_all)} machines)")
print(f"  FR + SR families total: {len(c1_all) + len(c2_all)} families ({sum(n for _, n, _ in c1_all) + sum(n for _, n, _ in c2_all)} machines)")
print(f"  Other FAST (FR == 0 & SRs < 10): {len(c3_other_fast)} families ({sum(n for _, n, _ in c3_other_fast)} machines)")
print(f"  Natural HALT rows: {len(halts_all)}")

# Save full collected rcands_rfull106.tsv and rhalts_rfull106.tsv
rcands_full_path = os.path.join(TRIAGE, 'rcands_rfull_all.tsv')
with open(rcands_full_path, 'w', encoding='utf-8') as o:
    o.write('class\tmachine\tfamily_size\tK\tnat_lg\tmaxcnt\tSRs\tSRK\tSRend\tSRsit_lg\tk2_lg\tFR\tshape\tchunk\n')
    for cls, lst in (('FR', c1_all), ('SR', c2_all)):
        for f, n, fn in lst:
            o.write('\t'.join([cls, f[0], str(n), f[1], f[3], f[4], f[6], f[8], f[9], f[10], f[11], f[16], f[17][:200], fn]) + '\n')

rhalts_full_path = os.path.join(TRIAGE, 'rhalts_rfull_all.tsv')
with open(rhalts_full_path, 'w', encoding='utf-8') as o:
    o.write('chunk\t' + '\t'.join([f'c{i}' for i in range(17)]) + '\n')
    for fn, f in halts_all:
        o.write(fn + '\t' + '\t'.join(f[:17]) + '\n')

# Check which chunk rcands_snap.tsv corresponded to
snap_machines = {r[1] for r in snap_rows}
chunk_hits = collections.Counter()
for fn, f in rows_all:
    if f[0] in snap_machines:
        chunk_hits[fn] += 1
print(f"rcands_snap.tsv machines come from chunks: {sorted(chunk_hits.keys())[0]} .. {sorted(chunk_hits.keys())[-1]} ({len(chunk_hits)} chunks)")
