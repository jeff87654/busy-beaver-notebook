"""symsuite.py: sound symbolic verification of every F5 macro rule on all 3 siblings (symsim, residue mod 2, A >= hlb).
For each case: symbolic config -> first template stop parsed (Lin) ; check: for 3 substitutions of the symbols (consistent
with residue, >= lb) the parsed config equals engine^k(config) for some k in 1..3 (k>1 only when symsim skipped D stops)."""
import sys, random, json
from fractions import Fraction as Fr
import symf5
from symf5 import run, Lin
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\never_audit')
from sym import mirror
from f5eng import step, show
MS = [('1RB1RG_0LC0LD_1RF0LD_0RE1LB_1LB0RF_0RA---_1RA1RD', 'D', True),
      ('1RB1RE_1RC1RA_0LD0LE_1RF0LE_0RG1LC_0RB---_1LC0RF', 'E', True),
      ('1RB0LD_0RC0RG_1LD0RG_0LE---_1LB1LF_1LE1LG_0LA1RB', 'G', False)]
def order(A, L, c):
    """symbol order = order of H tokens in build() (left to right in mirrored tape)"""
    names = []
    if c != -1 and isinstance(c, tuple): names.append('c')
    for idx in [len(L) - 1] + list(range(len(L) - 2, -1, -1)):
        if isinstance(L[idx], tuple): names.append('L%d' % idx)
    if isinstance(A, tuple): names.append('A')
    return names
def subst(A, L, c, vals):
    g = lambda x, k: vals[k] if isinstance(x, tuple) else x
    return (g(A, 'A'), tuple(g(x, 'L%d' % i) for i, x in enumerate(L)), g(c, 'c'))
def evalcfg(cf, env):
    A, L, c = cf; out = []
    for x in L:
        if isinstance(x, tuple):
            n = x[1].ev(env); assert n.denominator == 1 and n >= 0; out += [2] * int(n)
        else:
            v = x.ev(env); assert v.denominator == 1; out.append(int(v))
    return (int(A.ev(env)), tuple(out), int(c.ev(env)))
def check(M, q, A, L, c, lb, rng):
    r = run(M, q, A, L, c, mg=2, hlb=lb, maxstops=400, budget=2000000, tl=120)
    if r[0] != 'K': return 'NOK:' + str(r[1])[:200]
    names = order(A, L, c); res = r[1]
    for t in range(3):
        vals = {}
        for k in names:
            par = {'A': A, 'c': c}.get(k) if k in ('A', 'c') else L[int(k[1:])]
            vals[k] = lb + par[1] + 2 * rng.randrange(0, 40) if (lb + par[1]) % 2 == par[1] % 2 else lb + 1 + 2 * rng.randrange(0, 40)
            if vals[k] % 2 != par[1]: vals[k] += 1
        env = {'X%d' % i: vals[k] for i, k in enumerate(names)}
        st = subst(A, L, c, vals); got = evalcfg(res, env)
        cur = st; ok = False
        for k in range(4):
            cur, rule = step(cur)
            if cur is None: break
            if cur == got: ok = True; break
        if not ok: return 'MISMATCH %s -> sym %s' % (show(st), show(got))
    return 'OK'
if __name__ == '__main__':
    rng = random.Random(7)
    H0, H1 = ('H', 0), ('H', 1)
    js = list(range(1, 13)) + [16, 20, 25, 31]
    cases = []
    for j in js:
        lb = 2 * j + 12
        for c in (-1, H1, 1, 3):
            cases.append(('B-ord', j, lb, (H0, [0] * j + [H0, H0, H1], c)))       # ordinary source s>=2 even, then x, e
            cases.append(('B-ord2', j, lb, (H0, [0] * j + [2, 0, H1], c)))        # source 2 -> 0, zero after
            cases.append(('B-e', j, lb, (H0, [0] * j + [H1], c)))                 # attached odd source
            cases.append(('B-e0', j, lb, (H0, [0] * j + [H0], c)))                # attached even source
            cases.append(('M', j, lb, (H0, [0] * j + [1], c)))
            cases.append(('B-e3', j, lb, (H0, [0] * j + [3], c)))
            cases.append(('T', j, lb, (H0, [0] * j + [0], c)))
    for c in (-1, H1, 1, 3):
        cases.append(("T0", 0, 12, (H0, [0], c)))
        cases.append(("D", 0, 12, (H0, [H0, 0, H0, H1], c)))
        cases.append(("D1", 0, 12, (H0, [H1, H0, 0, H1], c)))
        cases.append(("De", 0, 12, (H0, [H1], c)))
        cases.append(("Me", 0, 12, (H0, [1], c)))   # e=1 at position 1: D then T0
    out = open(sys.argv[1], 'w')
    nbad = 0
    for M, q, mir in MS:
        Mm = mirror(M) if mir else M
        for kind, j, lb, (A, L, c) in cases:
            # concrete small c values are below lb: they are plain ints, fine
            r = check(Mm, q, A, L, c, lb, rng)
            if r != 'OK': nbad += 1
            out.write('%s\t%s\tj=%d\tlb=%d\tc=%s\t%s\n' % (M, kind, j, lb, c, r)); out.flush()
    out.write('DONE bad=%d\n' % nbad); out.close()
