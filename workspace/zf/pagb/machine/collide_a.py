"""Mechanical collision table for design A: every partition of the label set {a, b, c, d=c+1, 0} that
some parameter choice realizes, its gate status, the decoded effect on the bundle schemas (IND and the
five vacuity rows) and the quantified rows (ρ1, EX), and a semantic fuzz of the realized instances.

Usage: python collide_a.py [samples_per_partition]      writes runs/collide_a.txt and prints it.
"""
import sys, os, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault('PA_DESIGN', 'A')
import design, search_a as A, fuzz_a as F

LABS = ['a', 'b', 'c', 'u', 'd', '0']

def partitions(xs):
    if not xs: yield []; return
    x, rest = xs[0], xs[1:]
    for p in partitions(rest):
        for i in range(len(p)):
            yield p[:i] + [[x] + p[i]] + p[i + 1:]
        yield [[x]] + p

def realize(p, rnd):
    """concrete a, b, c realizing partition p, or None if impossible."""
    blk = {x: i for i, B in enumerate(p) for x in B}
    if blk['c'] == blk['d']: return None                     # c+1 ≠ c
    for _ in range(200):
        vals = {}
        zb = blk['0']; vals[zb] = 0
        cb = blk['c']; db = blk['d']
        if cb == zb:
            vals[cb] = 0
        else:
            vals.setdefault(cb, rnd.randint(1, 60))
        cv = vals[cb]
        if db in vals and vals[db] != cv + 1: continue
        vals[db] = cv + 1
        for B in range(len(p)):
            if B not in vals: vals[B] = rnd.randint(1, 70)
        if len(set(vals.values())) != len(p): continue
        env = {x: vals[blk[x]] for x in ['a', 'b', 'c', 'u']}
        if env['c'] + 1 != vals[db] or (blk['0'] in vals and vals[blk['0']] != 0): continue
        return env
    return None

def effect(p):
    blk = {x: i for i, B in enumerate(p) for x in B}
    same = lambda x, y: blk[x] == blk[y]
    if getattr(design, 'GATE', 'ab') != 'occ' and (same('c', 'a') or same('c', 'b') or same('c', 'u')):
        return 'gate closed: current := ⊤ (bundle not emitted)'
    if getattr(design, 'GATE', 'ab') == 'occ' and same('c', 'a'):
        e0 = ['c=a (label): IND(c,c,φ) valid without gate; GV: c ∉ vars T(a) by the gate']
    else:
        e0 = []
    e = list(e0)
    if same('a', 'b'): e.append('a=b: vacuity atoms become v_a==v_a, v_a==σv_a, v_a==v_a⊕v_d, v_a==v_a⊗v_d (instances); ρ1 = ∃a v_a==v_a')
    if same('a', 'd'): e.append('a=c+1: vacuity atoms v_d==v_b, v_d==v_b⊕v_d … (instances, c still ∉ atom)')
    if same('b', 'd'): e.append('b=c+1: vacuity atoms v_a==v_d, v_a==σv_d, v_a==v_d⊕v_d … (instances)')
    if same('a', '0'): e.append('a=0: IND/vacuity over v_0 (F is closed, no capture)')
    if same('b', '0'): e.append('b=0: atoms mention v_0 (instances)')
    if same('u', 'a') or same('u', 'b'): e.append('u∈{a,b}: ternary vacuity atoms v_a==v_b⊕v_u with repeated variables (instances)')
    if same('u', 'd'): e.append('u=c+1: third variable c+1 (instance)')
    if same('u', '0'): e.append('u=0: third variable v_0 (instance)')
    if same('c', '0'): e.append('c=0: φ = decode(0) = ⊤, IND trivial; vacuity binds v_0, which no atom contains (a,b ≠ 0, c+1 = 1)')
    return '; '.join(e) if e else 'all distinct (generic case)'

ARG = ('pprov (option a): the vacuity row is B6a for the atom T(a)==T(b), with v_c ∉ vars T(a) ∪ vars T(b) '
       'checked by the occurs-check gate; IND is pprov IND(a,c,φ): c ∉ φ by self-freshness, c ≠ a whenever a '
       'occurs in φ, and if a ∉ φ the instance is valid anyway (IND needs no gate); label identifications only '
       'produce instances; ρ1 is B7 for a variable term (also at a=b); EX is B7 with x=c+1 ∉ vars T(c).')

def main(nsamp=40):
    rnd = random.Random(2)
    roots = [design.BUNDLE] + [r for r in design.ROWS if r in (A.R1, A.EX)]
    lines = ['partition of {a,b,c,u,c+1,0} | gate (on realized values) | effect | fuzz (instances, FALSE)']
    total_false = 0; nparts = 0
    for p in partitions(LABS):
        env0 = realize(p, rnd)
        if env0 is None: continue
        nparts += 1
        import spec_pa
        gate = 'open' if spec_pa.gate_open(env0['a'], env0['b'], env0['c'], env0['u']) else 'closed'
        eff = effect(p) if gate == 'open' else 'gate closed (c ∈ vars of the gate terms): current := ⊤'
        n = nf = 0
        if gate == 'open':
            for _ in range(nsamp):
                env = realize(p, rnd); env.update(h=0)
                import spec_pa
                if not spec_pa.gate_open(env['a'], env['b'], env['c'], env['u']): continue
                for r in roots:
                    f = F.sem(r, env)
                    if F.qdepth(f) > 7: continue
                    n += 1
                    for _ in range(15):
                        vals = {}
                        rho = lambda j: vals.setdefault(j, rnd.randint(0, 4))
                        if not F.ev(f, rho, 6 if F.qdepth(f) <= 4 else 3):
                            nf += 1; break
        total_false += nf
        pt = ' '.join('{' + ','.join(B) + '}' for B in p)
        lines.append(f'{pt} | {gate} | {eff} | {n}, {nf}')
    lines.append(f'\n{nparts} realizable partitions; FALSE instances in total: {total_false}')
    lines.append('Argument (all open cases): ' + ARG)
    txt = '\n'.join(lines)
    open(os.path.join(HERE, 'runs', 'collide_a.txt'), 'w', encoding='utf-8').write(txt)
    print(txt)
    return total_false

if __name__ == '__main__':
    raise SystemExit(1 if main(*[int(x) for x in sys.argv[1:]]) else 0)
