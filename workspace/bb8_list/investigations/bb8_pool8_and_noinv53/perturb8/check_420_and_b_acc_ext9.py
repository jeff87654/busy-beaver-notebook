import collections, json, re, sys

BASE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_pool8_and_noinv53\perturb8'
sys.path.insert(0, BASE)
from analyze_ext9 import load_tsv
from classify_all_mut8_exact import parents, kl, run_from_k, parse_k
from evaluate_ext9_cls53 import parse_bk_det

rows = load_tsv('scan_ext9_cls53.tsv')

# Part 1: Check all 420 B1(l=1,p=1/1) B2(l=1,p=0/0) machines (and also B1(l=1,p=0/0) B2(l=1,p=1/1))
print("=== 1. CHECKING ALL B1(l=1) B2(l=1) OPPOSITE-PARITY MACHINES IN ext9_cls53 ===")
seen = set()
b1_b2_classes = collections.defaultdict(list)

for r in rows:
    pid, grp, mut, tm, epat, cat, binfo, btrace, det = r
    if tm in seen or cat not in ('B_HITS_HPAR', 'B_DEP_A_PAR!'):
        continue
    left_part = det.split(' | ')[0]
    tokens = {kv.split('=', 1)[0]: kv.split('=', 1)[1] for kv in left_part.split(' ') if '=' in kv}
    b1 = parse_bk_det(tokens.get('B1', ''))
    b2 = parse_bk_det(tokens.get('B2', ''))
    if not (b1 and b2):
        continue
    l1, p1 = len(b1[0][0]), b1[0][1] % 2
    l2, p2 = len(b2[0][0]), b2[0][1] % 2
    if l1 == 1 and l2 == 1 and p1 != p2:
        seen.add(tm)
        p = parents[pid]
        t = kl.tmpl(tm, p['tmpl_str'])
        B0 = p['B0']
        e_info = []
        d1_set = set()
        for a in (1, 3, 5, 7, 9, 11):
            er = run_from_k(tm, t, [], a, B0, req_B0=B0)
            if er[0] == 'K':
                ds, ao, _ = er[1]
                d1 = ds[0] if ds else -1
                has_z = (0 in ds)
                if len(ds) >= 3:
                    d1_set.add((d1, has_z))
                e_info.append(f"E{a}:L{len(ds)}(d1={d1},z={int(has_z)},a={ao})")
            else:
                e_info.append(f"E{a}:{er[0]}")
        sig = (p1, p2, tuple(sorted(d1_set)), " ".join(e_info[:4]))
        b1_b2_classes[sig].append(r)

print(f"Total opposite-parity B1(l=1)/B2(l=1) machines: {len(seen)} in {len(b1_b2_classes)} classes")
for sig, items in sorted(b1_b2_classes.items()):
    best = items[0]
    print(f"  count={len(items):3d} | B1_p={sig[0]} B2_p={sig[1]} d1_set(L>=3)={sig[2]} | {sig[3]}")
    print(f"    ex: {best[0]} {best[2]} ({best[6]} | {best[7]}) | {best[3]}")

# Part 2: Check all 1,429 B_ACC_OPEN machines in scan_ext9_cls53.tsv!
print("\n=== 2. CHECKING ALL B_ACC_OPEN MACHINES IN ext9_cls53 ===")
seen_b = set()
b_acc_classes = collections.defaultdict(list)
for r in rows:
    pid, grp, mut, tm, epat, cat, binfo, btrace, det = r
    if cat != 'B_ACC_OPEN' or tm in seen_b:
        continue
    seen_b.add(tm)
    # Group by (grp, epat, det)
    b_acc_classes[(grp, epat, det)].append(r)

print(f"Unique B_ACC_OPEN machines in ext9_cls53: {len(seen_b)} in {len(b_acc_classes)} rule classes")
for (grp, epat, det), items in sorted(b_acc_classes.items()):
    best = max(items, key=lambda x: (int(re.search(r'nE=(\d+)', x[6]).group(1)), int(re.search(r'maxL=(\d+)', x[6]).group(1))))
    print(f"  count={len(items):4d} | {grp:12s} | {epat} | best: {best[0]} {best[2]} {best[6]} {best[7]}")
    print(f"    tm={best[3]}")
    print(f"    det={det}")
