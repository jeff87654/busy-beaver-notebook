import collections, json, sys
BASE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_pool8_and_noinv53\perturb8'
sys.path.insert(0, BASE)
from evaluate_b_acc_exact import b_acc_tms, parents, kl, run_from_k, get_blank_k_seq

by_left_b = collections.defaultdict(list)
for src, r in b_acc_tms:
    pid, grp, mut, tm, epat, cat, binfo, btrace, det = r
    p = parents[pid]
    t = kl.tmpl(tm, p['tmpl_str'])
    lb1_10 = run_from_k(tm, t, [1, 0], 0, 10)
    lb1_11 = run_from_k(tm, t, [1, 0], 0, 11)
    lb2_10 = run_from_k(tm, t, [1, 0, 0], 0, 10)
    in_b1  = run_from_k(tm, t, [2, 0], 0, 10)
    in_d   = run_from_k(tm, t, [2], 0, 10)
    e67    = (run_from_k(tm, t, [], 0, 6)[:2], run_from_k(tm, t, [], 0, 7)[:2])
    sig = (str(in_d[:2]), str(in_b1[:2]), str(lb1_10[:2]), str(lb1_11[:2]), str(lb2_10[:2]), str(e67))
    by_left_b[(grp, sig)].append(r)

print(f"Distinct (grp, inner + leftmost borrow + E) signatures: {len(by_left_b)}")
for (grp, sig), items in sorted(by_left_b.items()):
    print(f"\n=== Group={grp} | count={len(items)} ===")
    print(f"  in_D(10)={sig[0]} | in_B1(10)={sig[1]}")
    print(f"  LEFT_B1(10)={sig[2]} | LEFT_B1(11)={sig[3]} | LEFT_B2(10)={sig[4]}")
    print(f"  E(0,6..7)={sig[5]}")
    for r in items[:4]:
        print(f"    * {r[0]} {r[2]} ({r[6]}) | {r[3]}")
