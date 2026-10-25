"""Design A (functional terms, Eq-atoms only): row ASTs, assembly, and order/label search.

Coding (see DESIGN.md): term T(0)=zero, 4P(t,1)+0=σt, 4P(t,u)+1=t⊕u, 4P(t,u)+2=t⊗u, 4P(i,0)+3=v_i.
Atoms: Eq-tag "T(m)==T(n)", Rel-tag "σT(m)==T(n)" (only F = Rel(0,0) = "σ0==0" uses it).
Usage: python search_a.py <seed> <iters> [tag]      (soundness-neutral choices only)
"""
import sys, os, json, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pagen import *
import pavars as P

def V(x): return ('V', x)
def S1(t): return ('S1', t)
def teq(t, u): return ('teq', t, u)
Z0 = 'Z0'
LAB = ['a', 'b', 'c', 'd', '0']

# ---- equality / term rows (arbitrary term codes a, b, c; no side conditions)
EUC = im(teq('c', 'a'), teq('c', 'b'), teq('a', 'b'))
CS = im(teq('a', 'b'), teq(S1('a'), S1('b')))
CA1 = im(teq('a', 'b'), teq(add('a', 'c'), add('b', 'c')))
CA2 = im(teq('a', 'b'), teq(add('c', 'a'), add('c', 'b')))
CM1 = im(teq('a', 'b'), teq(mul('a', 'c'), mul('b', 'c')))
CM2 = im(teq('a', 'b'), teq(mul('c', 'a'), mul('c', 'b')))
R1 = ex('a', teq(V('a'), V('b')))                 # ∃x x==y (flat)
EX = ex('d', teq(V('d'), 'c'))                    # ∃x x==T(c), x = c+1 ∉ vars(T(c))

def qaxioms(ch):
    out = []
    for i, (x, y) in enumerate(ch['qmap']):
        X, Y = V(x), V(y)
        out.append([no(teq(Z0, S1(X))),                              # zero_succ
                    im(teq(S1(X), S1(Y)), teq(X, Y)),                # succ_inj
                    teq(add(Z0, X), X),                              # add_zero
                    teq(add(S1(X), Y), S1(add(X, Y))),               # add_rec
                    teq(mul(Z0, X), Z0),                             # mult_zero
                    teq(mul(S1(X), Y), add(Y, mul(X, Y)))][i])       # mult_rec
    return out

def ng(lab):
    m, n, q, x = lab
    E = lambda s, t: teq(s, t)
    big = lambda y: no(E(V(y), mul(V(y), V(y))))
    pr = lambda y: an(big(y), al(m, al(n, im(E(V(y), mul(V(m), V(n))), orr(E(V(m), V(y)), E(V(n), V(y)))))))
    bad = no(al(x, im(orr(E(V(x), V(n)), E(V(x), V(q))), pr(x))))
    return ex(m, ex(n, ands(E(V(m), add(V(n), V(n))), big(n),
                            al(n, al(q, im(E(V(m), add(V(n), V(q))), bad))))))

# ---- gated bundle
IND = im(al('a', im(teq(V('a'), Z0), PHI)),
         al('a', im(PHI, al('c', im(teq(V('c'), S1(V('a'))), al('a', im(teq(V('a'), V('c')), PHI)))))),
         al('a', PHI))
def vac(A): return im(A, al('c', A))
VROWS = [vac(teq(V('a'), V('b'))), vac(teq(V('a'), S1(V('b')))), vac(teq(V('a'), Z0)),
         vac(teq(V('a'), add(V('b'), V('d')))), vac(teq(V('a'), mul(V('b'), V('d'))))]

NROWS = 19
def ng_of(ch):
    form = ch.get('ngform', 'cheap')
    if form == 'cheap': return ng(ch['nglab'])
    import ngw
    if form == 'literal': return ngw.ng_literal()
    if form == 'flat': return ngw.ng_flat(tuple(ch.get('numlab', ngw.NUM_LABELS)))
    return ngw.ng_alpha(ch['ngalpha'])           # 'alpha': binder names 2,4,6,8,10 -> ngalpha

def assemble(ch):
    rows = [P.L, EUC, P.B6C, P.COMM, P.QI, R1, EX, CS, CA1, CA2, CM1, CM2] + qaxioms(ch) + [ng_of(ch)]
    assert len(rows) == NROWS
    rows = [rows[i] for i in ch['rorder']]
    import pagen
    vacmode = ch.get('vac', 'pinned')
    pagen.REG4['on'] = (vacmode == 'b')
    pagen.OCC['on'] = (vacmode == 'a')
    if 'reg4pos' in ch: pagen.REG4['pos'] = ch['reg4pos']
    if vacmode == 'b':          # (b) unpinned: third variable = param4 (label 'u'), gate c ∉ {a,b,u}
        vr = [vac(teq(V('a'), V('b'))), vac(teq(V('a'), S1(V('b')))), vac(teq(V('a'), Z0)),
              vac(teq(V('a'), add(V('b'), V('u')))), vac(teq(V('a'), mul(V('b'), V('u'))))]
    elif vacmode == 'a':        # (a) general B6a on term codes a, b; occurs-check gate c ∉ vars T(a) ∪ vars T(b)
        vr = [vac(teq('a', 'b'))]
    else:
        vr = VROWS
    b = [IND] + vr
    if len(ch['border']) != len(b): ch = dict(ch, border=list(range(len(b))))
    b = [b[i] for i in ch['border']]
    return [P.GEN], rows, ands(*b)

def default_choice():
    return {'qmap': [['a', 'b']] * 6, 'nglab': ['1', '0', '3', '2'],
            'rorder': list(range(NROWS)), 'border': list(range(6))}

def random_choice(rng):
    return {'qmap': [rng.sample(LAB, 2) for _ in range(6)], 'nglab': rng.sample(['0', '1', '2', '3'], 4),
            'rorder': rng.sample(range(NROWS), NROWS), 'border': rng.sample(range(6), 6)}

def mutate(ch, rng):
    ch = json.loads(json.dumps(ch))
    k = rng.choice(['qmap', 'nglab', 'rorder', 'rorder', 'rorder', 'border'])
    if k == 'qmap':
        if ch.get('qpin'): return ch
        ch['qmap'][rng.randrange(6)] = rng.sample(LAB, 2)
    elif k in ('rorder', 'border'):
        o = ch[k]; i, j = rng.sample(range(len(o)), 2); o[i], o[j] = o[j], o[i]
    elif k == 'nglab' and ch.get('ngform') == 'alpha':
        ch['ngalpha'] = rng.sample(['0', '1', '2', '3', '4'], 5)
    else: ch[k] = random_choice(rng)[k]
    return ch

def score(ch, name):
    pre, post, b = assemble(ch)
    try:
        return build(name, pre, post, b)[0]
    except TypeError:          # TMBuilder bug in breakout_common_subsequences (self.reachable not called)
        return 10**6

if __name__ == '__main__':
    if os.name == 'nt':
        import ctypes
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
    seed, iters = int(sys.argv[1]), int(sys.argv[2])
    tag = sys.argv[3] if len(sys.argv) > 3 else 'A'
    rng = random.Random(seed)
    name = f'srcha_{tag}_{seed}'
    out = open(os.path.join(HERE, 'runs', f'search_a_{tag}_{seed}.jsonl'), 'w')
    cur = default_choice() if seed == 0 else random_choice(rng)
    if len(sys.argv) > 4:                       # extra fixed keys, e.g. '{"ngform": "literal"}'
        extra = json.loads(sys.argv[4]); cur.update(extra)
        if extra.get('qpin'): cur['qmap'] = [['0', '1']] * 6
    cs = score(cur, name); best = (cs, cur); stall = 0
    print('start', cs, flush=True)
    for it in range(iters):
        nxt = mutate(cur, rng); ns = score(nxt, name)
        if ns <= cs:
            if ns < cs: stall = 0
            cur, cs = nxt, ns
        else: stall += 1
        if cs < best[0]:
            best = (cs, cur); out.write(json.dumps({'states': cs, 'it': it, 'ch': cur}) + '\n'); out.flush()
            print('best', cs, it, flush=True)
        if stall > 400:
            cur = best[1]
            for _ in range(5): cur = mutate(cur, rng)
            cs = score(cur, name); stall = 0
    out.write(json.dumps({'final': best[0], 'ch': best[1]}) + '\n')
    try: os.remove(os.path.join(HERE, f'source_{name}.py'))
    except OSError: pass
    print('done', best[0], json.dumps(best[1]))
