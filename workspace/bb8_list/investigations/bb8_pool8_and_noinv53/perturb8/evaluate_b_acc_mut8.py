import collections, json, re, sys

BASE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_pool8_and_noinv53\perturb8'
sys.path.insert(0, BASE)
from classify_all_mut8_exact import all_rows, parents, kl, run_from_k, parse_k
from check_blank_first_k import get_blank_k_seq

seen = set()
b_acc_tms = []
for src, r in all_rows:
    pid, grp, mut, tm, epat, cat, binfo, btrace, det = r
    if cat == 'B_ACC_OPEN' and tm not in seen:
        seen.add(tm)
        b_acc_tms.append((src, r))

print(f"Total unique B_ACC_OPEN machines: {len(b_acc_tms)}")

for src, r in b_acc_tms:
    pid, grp, mut, tm, epat, cat, binfo, btrace, det = r
    p = parents[pid]
    t = kl.tmpl(tm, p['tmpl_str'])
    ks = get_blank_k_seq(tm, t, maxs=50000, req_B0=None)
    # Check D at a=0,1,2,3 and b=10,11
    d0 = run_from_k(tm, t, [3], 0, 10)
    d2 = run_from_k(tm, t, [3], 2, 10)
    b1_0 = run_from_k(tm, t, [2, 0], 0, 10)
    b1_1 = run_from_k(tm, t, [2, 0], 1, 10)
    print(f"\n* {pid:14s} {grp:12s} {mut:16s} | {tm}")
    print(f"  binfo={binfo} | btrace={btrace}")
    print(f"  det={det}")
    print(f"  D(a=0,b=10)->{d0[1] if d0[0]=='K' else d0[0]} | D(a=2,b=10)->{d2[1] if d2[0]=='K' else d2[0]}")
    print(f"  B1(a=0,b=10)->{b1_0[1] if b1_0[0]=='K' else b1_0[0]} | B1(a=1,b=10)->{b1_1[1] if b1_1[0]=='K' else b1_1[0]}")
    for st, k in ks[:5]:
        print(f"    st={st:6d}: ds={k[0]} (len={len(k[0])}), a={k[1]}, b={k[2]}")
    # Also check E(a=0, b) and E(a=1, b) for b=6..11
    e_list = []
    for a in (0, 1):
        for b in (6, 7, 8, 9):
            er = run_from_k(tm, t, [], a, b)
            e_list.append(f"E({a},{b}):{er[1] if er[0]=='K' else er[0]}")
    print(f"  E: {' | '.join(e_list)}")
