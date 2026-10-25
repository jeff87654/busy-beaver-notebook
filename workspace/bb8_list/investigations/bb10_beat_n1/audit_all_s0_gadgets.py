"""Test all 5,792 alternative S0 gadgets from search_n1_gadgets.py using exact R1/R2 macro-acceleration
to see if ANY gadget besides n1 and n1_plus1 produces a multi-period (f_{omega+1}) countdown or halts with a larger score."""
import re
from search_n1_gadgets import BASE_TR, OPTS_E0, OPTS_IJ, bword, toks, run_lazy, fmt_tr

def step_macro_or_tm(tr, far_toks, L, A, max_tm_steps=1500):
    """If L ends with [..., t] + [1]*k where t >= 3, apply exact R1/R2 macro step.
    Otherwise, materialize the active suffix (plus enough left context from L/far_toks) and run literal TM to next B-form."""
    # Find trailing 1s
    k = 0
    while k < len(L) and L[len(L) - 1 - k] == 1:
        k += 1
    if k < len(L):
        t = L[len(L) - 1 - k]
        if t >= 3:
            idx = len(L) - 1 - k
            if k == 0:
                m, r = divmod(t, 3)
                L_new = L[:idx] + [r]
                A_new = (A + 8) * (1 << m) - 8
                if A_new > 10**6:
                    return 'HUGE_A', (far_toks, L_new, A_new)
                return 'B', (far_toks, L_new, A_new)
            else:
                L_new = L[:idx] + [t - 3, A + 3] + [1] * (k - 1)
                return 'B', (far_toks, L_new, 4)
    # Need literal TM step! Reconstruct word from far_toks + L + [0, A]
    # To keep literal TM fast, cap A if A is huge
    if A > 2000:
        return 'HUGE_A', (far_toks, L, A)
    far_str = ''.join(('0' * int(x[1:])) if isinstance(x, str) else ('10' * x + '1') for x in far_toks)
    wd = bword(L, A, far_str)
    kind, res = run_lazy(tr, wd, want_halt=False, maxsteps=max_tm_steps)
    if kind == 'B':
        return 'B', (res[0], res[1], res[2])
    return kind, res

def main():
    w_s0 = bword([2] + [1]*8 + [0, 1, 1, 1], 6)
    TR_N1 = dict(BASE_TR)
    TR_N1[('E', 0)] = (1, -1, 'I')
    TR_N1[('I', 0)] = (0, -1, 'J')
    TR_N1[('I', 1)] = (0, -1, 'I')
    TR_N1[('J', 0)] = None
    TR_N1[('J', 1)] = (0, -1, 'C')
    _, r_s0 = run_lazy(TR_N1, w_s0, want_halt=False, maxsteps=2000)
    exp_s0 = r_s0[:3]

    alt_gadgets = []
    def dfs_s0(tr):
        kind, res = run_lazy(tr, w_s0, want_halt=False, maxsteps=1000)
        if kind == 'BRANCH':
            key = res
            used_ij = sum(1 for q in ('I', 'J') for b in (0, 1) if (q, b) in tr)
            if key != ('E', 0) and used_ij >= 3:
                return
            opts = OPTS_E0 if key == ('E', 0) else OPTS_IJ
            for o in opts:
                tr2 = dict(tr)
                tr2[key] = o
                dfs_s0(tr2)
            return
        if kind == 'B':
            if res[:3] != exp_s0:
                alt_gadgets.append((dict(tr), (tuple(res[0]), tuple(res[1]), res[2])))

    dfs_s0(dict(BASE_TR))
    print(f"Collected {len(alt_gadgets)} alt S0 gadgets across {len(set(x[1] for x in alt_gadgets))} S0 shapes.")

    # Group by S0 shape and test representative (or all) on a longer list [2, 1^24, 0, 1^3 | 6]
    # Also allow lazy branching if a new IJ slot is hit later!
    outcomes = {}
    interesting = []

    def sim_Validation(tr, far_toks, L, A, depth=0):
        for step in range(400):
            # Check if all zeros in L have been eliminated (meaning we returned to a pure >0 list -> new period / H!)
            if 0 not in L and len(L) > 0:
                return 'PURE_LIST', (far_toks, L, A, step)
            kind, res = step_macro_or_tm(tr, far_toks, L, A)
            if kind == 'B':
                far_toks, L, A = res
                continue
            if kind == 'BRANCH':
                key = res
                used_ij = sum(1 for q in ('I', 'J') for b in (0, 1) if (q, b) in tr)
                if key != ('E', 0) and used_ij >= 3:
                    # Must be HALT (None) on this slot!
                    return 'HALT_AT_BRANCH', (key, far_toks, L, A, step)
                # Try None (HALT) and all OPTS_IJ
                results = [('HALT_AT_BRANCH', (key, far_toks, L, A, step))]
                for o in OPTS_IJ:
                    tr2 = dict(tr)
                    tr2[key] = o
                    r2 = sim_Validation(tr2, far_toks, L, A, depth + 1)
                    results.append((o, r2))
                return 'BRANCHED', results
            return kind, (res, far_toks, L, A, step)
        return 'MAX_MACRO_STEPS', (far_toks, L, A)

    # First test one representative per S0 shape (Wait: if an S0 shape already used 3 IJ slots, all gadgets in that shape have identical defined transitions on the path!)
    # Wait: what if two gadgets in the same S0 shape defined different transitions? No, lazy DFS only defines transitions that were ACTUALLY USED during S0!
    # Wait: two different gadgets can produce the SAME S0 shape, and behave differently later if they hit a state/symbol they defined differently!
    # So let's test ALL 5,792 alt_gadgets!
    for idx, (tr, s0_shape) in enumerate(alt_gadgets):
        res = sim_Validation(tr, [], [2] + [1]*24 + [0, 1, 1, 1], 6)
        k = res[0]
        outcomes[k] = outcomes.get(k, 0) + 1
        if k in ('PURE_LIST', 'HUGE_A', 'BRANCHED'):
            interesting.append((tr, s0_shape, res))

    print("Outcomes across all 5,792 alt S0 gadgets on [2, 1^24, 0, 1^3 | 6]:", outcomes)
    print(f"Interesting count: {len(interesting)}")
    for tr, s0_shape, res in interesting[:40]:
        print(f"  {fmt_tr(tr):32s} | res={res[0]} | details={str(res[1])[:120]}")

if __name__ == '__main__':
    main()
