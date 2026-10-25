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

# Let's check for each unique B_ACC_OPEN machine:
# 1. Does any mutation change D, B1, B2, B3, or E from its parent, or only blank startup (or B0)?
by_rules = collections.defaultdict(list)
for src, r in b_acc_tms:
    pid, grp, mut, tm, epat, cat, binfo, btrace, det = r
    p = parents[pid]
    t = kl.tmpl(tm, p['tmpl_str'])
    # Test [2],0,10 (inner D), [1],0,10 and [1],0,11 (final D before E!), [2,0],0,10 (B1), and E(0,6..9)
    r_in_10 = run_from_k(tm, t, [2], 0, 10)
    r_in_11 = run_from_k(tm, t, [2], 0, 11)
    r_fin_10 = run_from_k(tm, t, [1], 0, 10)
    r_fin_11 = run_from_k(tm, t, [1], 0, 11)
    r_b1_10 = run_from_k(tm, t, [2, 0], 0, 10)
    r_b1_11 = run_from_k(tm, t, [2, 0], 0, 11)
    r_b2_10 = run_from_k(tm, t, [2, 0, 0], 0, 10)
    e_6_9 = [run_from_k(tm, t, [], 0, b) for b in (6, 7, 8, 9)]
    sig = (
        str(r_in_10[:2]), str(r_in_11[:2]),
        str(r_fin_10[:2]), str(r_fin_11[:2]),
        str(r_b1_10[:2]), str(r_b1_11[:2]),
        str(r_b2_10[:2]),
        tuple(str(x[:2]) for x in e_6_9)
    )
    ks = get_blank_k_seq(tm, t, maxs=50000, req_B0=None)
    by_rules[(grp, sig)].append((r, ks))

print(f"Distinct (grp, inner/final/B1/B2/E rules) among B_ACC_OPEN: {len(by_rules)}")
for (grp, sig), items in sorted(by_rules.items()):
    print(f"\n=== Group={grp} | count={len(items)} ===")
    print(f"  [2],0,10 -> {sig[0]} | [2],0,11 -> {sig[1]}")
    print(f"  [1],0,10 -> {sig[2]} | [1],0,11 -> {sig[3]}")
    print(f"  B1(10)   -> {sig[4]} | B1(11)   -> {sig[5]}")
    print(f"  B2(10)   -> {sig[6]}")
    print(f"  E(0,6..9)-> {sig[7]}")
    seen_k = set()
    for r, ks in items:
        k_str = " -> ".join(f"{k[0]}(a={k[1]},b={k[2]})" for _, k in ks[:5])
        if k_str not in seen_k:
            seen_k.add(k_str)
            print(f"    * {r[0]} {r[2]} ({r[6]}) | {r[3]}")
            print(f"      startup: {k_str}")
