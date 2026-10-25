import collections, json, re, sys

BASE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_pool8_and_noinv53\perturb8'
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import bcfg, kl
from check_exact_multiround_rules import load_tsv, parents, run_from_k, parse_k

cls53_rows = load_tsv('scan_mut8_cls53.tsv')
cand_rows = load_tsv('scan_mut8_cand162.tsv')
all_rows = [('cls53', r) for r in cls53_rows] + [('cand162', r) for r in cand_rows]

# Part 1: Symbolic / exact multi-round fate of all 252 unique a_acc machines in B_HITS_HPAR / B_DEP_A_PAR! / NON_MOD2_E!
# Notice: in a_acc with D(a) = c*a + d where c is odd (3 or 5) and d is even (4 or 6), D preserves parity of a!
# Let's write a recursive memoized function `final_parity(ds_tuple, a_par)` that computes the exact parity of `a`
# when `ds_tuple` is reduced to all zeros `(0, ..., 0)`!
# Wait: for a tuple `ds = (d_1, ..., d_m)`:
# - If all d_i == 0: return a_par.
# - If d_m > 0: since D preserves parity of a, reducing d_m -> 0 leaves a_par unchanged!
#   Wait: what if B_k (when d_m == 0) depends on the numeric value of `a` (in the new list entry `c_1(a) = 3a+c` or `5a+c`)?
#   Since D preserves `a_par`, ANY positive value `d >= 1` in `ds` when reduced to `0` by repeating `1 -> 0` `d` times:
#   Wait: after the FIRST step `d -> d-1`, the new parity `p1` is independent of `d`, and the remaining `d-1` steps
#   each start with parity `p1` and end with parity `p2`!
#   In fact, for ANY deterministic map f: {0, 1} -> {0, 1}, applying f `d` times to `p`:
#   - If f(0)==0 and f(1)==0: f^d(p) = 0 for all d >= 1!
#   - If f(0)==1 and f(1)==1: f^d(p) = 1 for all d >= 1!
#   - If f(0)==0 and f(1)==1: f^d(p) = p for all d >= 1!
#   - ONLY if f(0)==1 and f(1)==0 (negation!) does f^d(p) depend on `d % 2`!
# Let's check if ANY B_HITS_HPAR or B_DEP_A_PAR! machine EVER has a negation map f(0)=1, f(1)=0!

def analyze_a_acc_symbolic(tm, p):
    t = kl.tmpl(tm, p['tmpl_str'])
    B0 = p['B0']
    # Check D parity map
    r4 = run_from_k(tm, t, [3], 4, B0, req_B0=B0)
    r5 = run_from_k(tm, t, [3], 5, B0, req_B0=B0)
    if r4[0] != 'K' or r5[0] != 'K':
        return "BAD_D"
    da = r5[1][1] - r4[1][1]
    ca = r4[1][1] - 4 * da
    if da % 2 == 1 and ca % 2 == 1:
        return "MOD3_GATE_HALT_E2 (5a+7, E(3m)=H)"

    # Check B_k for k=1..6 at a=5 (odd) and a=6 (even)
    b_rules = {}
    for k in range(1, 7):
        rk_even = run_from_k(tm, t, [2] + [0]*k, 6, B0, req_B0=B0)
        rk_odd  = run_from_k(tm, t, [2] + [0]*k, 5, B0, req_B0=B0)
        if rk_even[0] != 'K' or rk_odd[0] != 'K':
            return f"B{k}_NON_K"
        ds_e, a_e, _ = rk_even[1]
        ds_o, a_o, _ = rk_odd[1]
        # ds_e[0] should be 1
        if not ds_e or ds_e[0] != 1 or not ds_o or ds_o[0] != 1:
            return f"B{k}_BAD_PREFIX"
        tail_e = ds_e[1:]
        tail_o = ds_o[1:]
        # Check if B_k increases tuple length (len(tail) > k)
        if len(tail_e) > k or len(tail_o) > k:
            # Wait: if B1 increases tuple length (len(tail) > 1), then every B1 makes the tuple longer!
            if k == 1:
                return f"RUNAWAY_B1 (|L1|={len(tail_e)}>1, list grows forever in single round)"
        b_rules[k] = {
            0: (tail_e, a_e % 2, a_e),
            1: (tail_o, a_o % 2, a_o),
        }

    # Check if B1 is terminating (len(tail) <= 1)
    # Compute parity transformer F_k(a_par) for reducing (..., 1, 0^k) -> (..., 0, 0^k)
    # Wait: if len(tail) == k, reducing (..., 1, 0^k) replaces it by (..., 0, tail_1, ..., tail_k).
    # What if len(tail) < k? Then the tuple length SHRINKS by k - len(tail)!
    # Let's simulate the tuple reduction where each positive entry > 0 is replaced by '+' (since we check if f is constant/identity)!
    return b_rules

seen = set()
summary = collections.Counter()
for src, r in all_rows:
    pid, grp, mut, tm, epat, cat, binfo, btrace, det = r
    if tm in seen or cat not in ('B_HITS_HPAR', 'B_DEP_A_PAR!', 'NON_MOD2_E!'):
        continue
    seen.add(tm)
    p = parents[pid]
    res = analyze_a_acc_symbolic(tm, p)
    if isinstance(res, str):
        summary[res] += 1
        continue
    # res is b_rules for k=1..6
    # Let's check B1, B2, B3 lengths and parities
    b1_len = len(res[1][0][0])
    b1_p0, b1_p1 = res[1][0][1], res[1][1][1]
    b2_len = len(res[2][0][0])
    b2_p0, b2_p1 = res[2][0][1], res[2][1][1]
    b3_len = len(res[3][0][0])
    b3_p0, b3_p1 = res[3][0][1], res[3][1][1]
    key = f"B1(len={b1_len},p={b1_p0}/{b1_p1}) B2(len={b2_len},p={b2_p0}/{b2_p1},tail={res[2][0][0][1:]}) B3(len={b3_len},p={b3_p0}/{b3_p1},tail={res[3][0][0][1:]})"
    summary[key] += 1

print("=== SUMMARY OF ALL 252 UNIQUE B_HITS_HPAR / B_DEP_A_PAR! / NON_MOD2_E! MACHINES ===")
for k, v in sorted(summary.items()):
    print(f"  {v:3d}x : {k}")
