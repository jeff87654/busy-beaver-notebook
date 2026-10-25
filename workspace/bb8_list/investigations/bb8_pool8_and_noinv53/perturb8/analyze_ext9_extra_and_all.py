import os, json, re, collections, sys, ctypes

try:
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00000040)
except Exception:
    pass

BASE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_pool8_and_noinv53\perturb8'
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import bcfg, kl

def load_tsv(fn):
    path = BASE + '\\' + fn
    raw = open(path, 'rb').read()
    text = raw.decode('utf-16' if raw.startswith(b'\xff\xfe') else 'utf-8', errors='ignore')
    rows = []
    for line in text.splitlines():
        parts = line.rstrip('\r\n').split('\t')
        if len(parts) >= 9:
            rows.append(parts[:9])
    return rows

extra_rows = load_tsv('scan_ext9_extra.tsv')
cls53_rows = load_tsv('scan_ext9_cls53.tsv')
cand_rows  = load_tsv('scan_ext9_cand162.tsv')

print(f"Loaded extra={len(extra_rows)}, cls53={len(cls53_rows)}, cand162={len(cand_rows)}")

# 1. Inspect ALL mod3_e and mod3_g rows in extra_rows!
mod3_rows = [r for r in extra_rows if r[0].startswith('mod3_')]
print(f"\n=== 1. MOD3 EXT9 SURVIVORS ({len(mod3_rows)} rows) ===")
by_mod3_sig = collections.defaultdict(list)
for r in mod3_rows:
    pid, grp, mut, tm, epat, cat, binfo, btrace, det = r
    by_mod3_sig[(epat, cat, det)].append(r)

for (epat, cat, det), items in sorted(by_mod3_sig.items()):
    r0 = items[0]
    print(f"  count={len(items):3d} | {epat} | {cat} | sample: {r0[0]} {r0[2]} {r0[6]} {r0[7]} | {r0[3]}")
    print(f"    det={det}")

# 2. Check all NON_MOD2_E! or unusual epats in extra_rows and cand_rows
print("\n=== 2. UNUSUAL EPATS OR NON_MOD2_E! IN EXTRA & CAND162 ===")
for src, rows in [('extra', extra_rows), ('cand162', cand_rows)]:
    c_epat = collections.Counter(r[4] for r in rows)
    c_cat  = collections.Counter(r[5] for r in rows)
    print(f"  {src}: epats={dict(c_epat)} | cats={dict(c_cat)}")
    seen = set()
    for r in rows:
        pid, grp, mut, tm, epat, cat, binfo, btrace, det = r
        if tm in seen:
            continue
        if epat not in ('HKHKHKHK', 'KHKHKHKH') and not pid.startswith('mod3_'):
            seen.add(tm)
            print(f"    [{src}] {pid} {mut} | {epat} {cat} | {binfo} {btrace} | {tm}")
            print(f"      det={det}")

# 3. Check top maxL and nE in extra_rows and cand_rows
print("\n=== 3. TOP maxL / nE IN EXTRA & CAND162 (B_HITS_HPAR / B_DEP_A_PAR! / NON_MOD2_E!) ===")
for src, rows in [('extra', extra_rows), ('cand162', cand_rows)]:
    interesting = [r for r in rows if r[5] in ('B_HITS_HPAR', 'B_DEP_A_PAR!', 'NON_MOD2_E!')]
    by_det = collections.defaultdict(list)
    for r in interesting:
        # group by (epat, cat, B1..B3 part of det)
        bpart = r[8].split(' | E:')[0]
        by_det[(r[4], r[5], bpart)].append(r)
    print(f"  {src}: {len(interesting)} rows in {len(by_det)} B-structural groups")
    for (epat, cat, bpart), items in sorted(by_det.items()):
        best = max(items, key=lambda x: (int(re.search(r'nE=(\d+)', x[6]).group(1)), int(re.search(r'maxL=(\d+)', x[6]).group(1))))
        e_part = best[8].split(' | E:')[1] if ' | E:' in best[8] else ''
        print(f"    {len(items):4d}x [{cat}] {epat} | {bpart}")
        print(f"          best: {best[0]} {best[2]} {best[6]} {best[7]} | {best[3]} | E:{e_part[:60]}")
