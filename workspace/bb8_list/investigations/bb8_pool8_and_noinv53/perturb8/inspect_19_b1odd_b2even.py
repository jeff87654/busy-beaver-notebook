import collections, json, re, sys

BASE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_pool8_and_noinv53\perturb8'
sys.path.insert(0, BASE)
from classify_all_mut8_exact import all_rows, parents, analyze_a_acc_symbolic, kl, run_from_k

seen = set()
for src, r in all_rows:
    pid, grp, mut, tm, epat, cat, binfo, btrace, det = r
    if tm in seen or cat not in ('B_HITS_HPAR', 'B_DEP_A_PAR!'):
        continue
    seen.add(tm)
    p = parents[pid]
    res = analyze_a_acc_symbolic(tm, p)
    if isinstance(res, str):
        continue
    b1_len = len(res[1][0][0])
    b1_p0, b1_p1 = res[1][0][1], res[1][1][1]
    b2_len = len(res[2][0][0])
    b2_p0, b2_p1 = res[2][0][1], res[2][1][1]
    if b1_len == 1 and b1_p0 == 1 and b2_len == 1 and b2_p0 == 0:
        t = kl.tmpl(tm, p['tmpl_str'])
        B0 = p['B0']
        print(f"\n* {pid} {mut} | {tm}")
        print(f"  binfo={binfo} | btrace={btrace}")
        print(f"  det={det}")
        # Check E(a) for a=1, 2, 3, 4, 5, 6, 7
        for a in range(1, 8):
            er = run_from_k(tm, t, [], a, B0, req_B0=B0)
            if er[0] == 'K':
                print(f"    E({a}): K ds={er[1][0]} (len={len(er[1][0])}), a_out={er[1][1]}")
            else:
                print(f"    E({a}): {er[0]} at {er[1]}")
