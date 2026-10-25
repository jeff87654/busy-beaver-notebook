"""Exhaustively test all 1-slot and 2-slot mutations of the 15 base transitions (A0..H1 minus E0),
including transitions to A..H and to I, J (under both n1 and n1_plus1 IJ gadgets), to check:
1) Which mutations preserve the Ackermann clearing rules R1 and R2 (or a generalized R1/R2 clearing engine), and
2) What initial B-form B(L, A) each such machine produces from a blank tape!"""
import itertools
from test_n1_twins import parse_tm, Tape, run_to_b, bword

BASE_GH  = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_---0LJ_0LE0LJ'
BASE_REC = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LJ_0LE0LJ'

BASE_KEYS = [(q, s) for q in 'ABCDEFGH' for s in (0, 1) if (q, s) != ('E', 0)]
ALL_OPTS = [(w, d, q) for w in (0, 1) for d in (-1, 1) for q in 'ABCDEFGHIJ']

def fast_from_b(tr, L, A, cs, maxsteps=400):
    w = bword(L, A)
    return run_to_b(tr, w, len(w), cs, cs, maxsteps=maxsteps)

def check_r1_r2(tr, cs):
    # First check small instance (takes ~130 steps) with maxsteps=600:
    kind, r = fast_from_b(tr, [2, 4], 1, cs, maxsteps=600)
    if kind != 'B' or r[1] != ([], [2, 1], 10):
        return False
    # Now check larger instances with maxsteps=3000:
    kind, r = fast_from_b(tr, [2, 7], 4, cs, maxsteps=3000)
    if kind != 'B' or r[1] != ([], [2, 4], 16):
        return False
    for t, k, A in [(1, 1, 1), (3, 2, 4)]:
        kind, r = fast_from_b(tr, [2, t + 3] + [1]*(k + 1), A, cs, maxsteps=3000)
        if kind != 'B' or r[1] != ([], [2, t, A + 3] + [1]*k, 4):
            return False
    return True

def check_startup(tr, cs, maxsteps=30000):
    T = Tape(tr, '0', 0, 'A', cs)
    best_b = None
    while T.steps < maxsteps:
        if not T.step():
            return 'HALT', T.steps
        if T.q == cs and T.t[T.h] == 0 and T.t[T.h - 1] == 1:
            bf = T.bform()
            if bf and bf[0] == []:
                L, A = bf[1], bf[2]
                if len(L) >= 10 and all(x == 1 for x in L[1:]):
                    return 'START_LIST', (T.steps, L[0], len(L) - 1, A)
                best_b = (T.steps, len(L), L[:5], A)
    return 'NO_START_LIST', best_b

def fmt_diff(base_tr, tr):
    diffs = []
    for k in BASE_KEYS:
        if tr[k] != base_tr[k]:
            w, d, q = tr[k]
            diffs.append(f"{k[0]}{k[1]}={w}{'R' if d==1 else 'L'}{q}")
    return ','.join(diffs) or 'NONE'

def main():
    for bname, bm, cs in [('GH', BASE_GH, 'H'), ('REC', BASE_REC, 'G')]:
        base_tr = parse_tm(bm)
        assert check_r1_r2(base_tr, cs), f"Base {bname} failed check_r1_r2!"
        print(f"=== Testing 1-slot mutations of {bname} (15 keys x 40 opts = 600) ===")
        r12_1 = []
        for k in BASE_KEYS:
            for o in ALL_OPTS:
                if o == base_tr[k]:
                    continue
                tr = dict(base_tr)
                tr[k] = o
                if check_r1_r2(tr, cs):
                    st_res = check_startup(tr, cs)
                    r12_1.append((fmt_diff(base_tr, tr), st_res))
        print(f"  1-slot mutations preserving R1 & R2: {len(r12_1)}")
        for d, sr in r12_1:
            print(f"    {d:20s} -> {sr}")

        # Test ALL 105 2-slot mutations across all 15 base keys using lazy branching on R1 & R2!
        print(f"=== Testing ALL 105 pairs of 2-slot mutations of A..H in {bname} via lazy branching ===", flush=True)
        w_r1 = bword([2, 4], 1)
        exp_r1 = ([], [2, 1], 10)
        w_r2 = bword([2, 4, 1, 1], 1)
        exp_r2 = ([], [2, 1, 4, 1], 4)

        def run_lazy_cs(tr, word, exp, cs, maxsteps=300):
            T = Tape(tr, word, len(word), cs, cs)
            while T.steps < maxsteps:
                key = (T.q, T.t[T.h])
                if key not in tr:
                    return 'BRANCH', key
                if not T.step():
                    return 'HALT', None
                if T.q == cs and T.t[T.h] == 0 and T.t[T.h - 1] == 1:
                    bf = T.bform()
                    if bf is not None:
                        return 'B', bf
            return 'TIME', None

        r12_2 = []
        for k1, k2 in itertools.combinations(BASE_KEYS, 2):
            tr0 = dict(base_tr)
            del tr0[k1]
            del tr0[k2]

            def dfs2(tr, stg):
                wd, exp = (w_r1, exp_r1) if stg == 0 else (w_r2, exp_r2)
                kind, res = run_lazy_cs(tr, wd, exp, cs)
                if kind == 'BRANCH':
                    for o in ALL_OPTS:
                        tr2 = dict(tr)
                        tr2[res] = o
                        dfs2(tr2, stg)
                    return
                if kind == 'B' and res == exp:
                    if stg == 0:
                        dfs2(tr, 1)
                    else:
                        # Fill any unbranched key with base_tr, skip if <2 diffs from base_tr
                        for kk in (k1, k2):
                            if kk not in tr:
                                tr[kk] = base_tr[kk]
                        if tr[k1] != base_tr[k1] and tr[k2] != base_tr[k2]:
                            if check_r1_r2(tr, cs):
                                st_res = check_startup(tr, cs)
                                r12_2.append((fmt_diff(base_tr, tr), st_res))

            dfs2(tr0, 0)
        print(f"  2-slot A..H mutations preserving R1 & R2: {len(r12_2)}", flush=True)
        for d, sr in r12_2:
            print(f"    {d:25s} -> {sr}", flush=True)

if __name__ == '__main__':
    main()
