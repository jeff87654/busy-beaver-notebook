"""symsuite68.py: sound symbolic (symsim) verification of every F68 macro rule (mirrored machine, K = D event on the right
after mirroring), residue mod 2, symbols >= hlb.  Check: for 3 substitutions of the symbols the parsed symsim result equals
engine^k(config) for k in 1..3.  argv: out.tsv  mode ('safe': hlb=j+1 = safety-lemma bound; 'exact': hlb=max(j-1,0))."""
import sys, random
import symf68
from symf68 import run, Lin
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\never_audit')
from sym import mirror
from f68eng import step, show
M68 = '1RB1RE_0LC0LD_1RF0LD_1LE1LB_1RA1RG_1RE---_0RC0RF'
def order(A, L, c):
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
            n = x[1].ev(env); assert n.denominator == 1 and n >= 0; out += [1] * int(n)
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
            par = A if k == 'A' else (c if k == 'c' else L[int(k[1:])])
            v = lb + 2 * rng.randrange(0, 40)
            if v % 2 != par[1]: v += 1
            vals[k] = v
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
    FULL = sys.argv[2] == 'full'; JS = [int(x) for x in sys.argv[3].split(',')]
    H0, H1 = ('H', 0), ('H', 1)
    cases = []
    for j in JS:
        lb = max(j + 4, 6)
        As = [H0, H1] + (list(range(max(j - 1, 0), lb)) if FULL else [])          # symbolic A >= lb, plus every concrete A in [j-1, lb)
        for A in As:
            for s in ((H0, H1, 1, 2, 3, 4, 5) if FULL else (H0, H1, 1)):
                for tail in ([H0, H1], [0, H1], [1], [0, 0, 1], []):
                    cases.append(('B', j, lb, (A, [0]*j + [s] + tail, -1)))
            cases.append(('T', j, lb, (A, [0]*(j + 1), -1)))
    for A in [H0, H1] + list(range(0, 6)):
        cases += [('T0', 0, 6, (A, [0], -1)), ('D', 0, 6, (A, [H0, 0, H1], -1)), ('D1', 0, 6, (A, [H1, 1, 1], -1)), ('D2', 0, 6, (A, [1, 0, 1], -1))]
    out = open(sys.argv[1], 'w'); nbad = 0; Mm = mirror(M68)
    for kind, j, lb, (A, L, c) in cases:
        r = check(Mm, 'D', A, L, c, lb, rng)
        if r != 'OK': nbad += 1
        out.write(chr(9).join((kind, 'j=%d' % j, 'lb=%d' % lb, 'A=%s' % (A,), 'L=%s' % (L,), r)) + chr(10)); out.flush()
    out.write('DONE cases=%d bad=%d' % (len(cases), nbad) + chr(10)); out.close()
