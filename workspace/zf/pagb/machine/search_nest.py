"""INVALID: nested terms cannot be encoded in the 4-tag coding (bare var v_i = integer i collides
with truth/F/zero and with sigma(v0)). Kept only to document the dead end; do not use. Use search_pa (FLAT)."""
"""Order/label search for the NESTED-TERMS PA variant (atoms Eq(t,u) only; terms nested).
Reuses pagen; soundness-neutral choices: Q-axiom relabelings, NG labels, row/bundle order,
term congruence row labels.  python search_nest.py <seed> <iters> [tag]
"""
import sys, os, json, random, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pagen import *
import pavars as P

LAB = ['a', 'b', 'c', 'd', '0']
def eqt(t, u): return ('eq', t, u)

def relabel(f, m):
    if isinstance(f, str): return m.get(f, f)
    if isinstance(f, tuple): return (f[0],) + tuple(relabel(x, m) for x in f[1:])
    return f

def qaxioms(ch):
    x, y = 'x', 'y'
    base = [no(eqt('Z', S(x))),
            im(eqt(S(x), S(y)), eqt(x, y)),
            eqt(add('Z', x), x),
            eqt(add(S(x), y), S(add(x, y))),
            eqt(mul('Z', x), 'Z'),
            eqt(mul(S(x), y), add(y, mul(x, y)))]
    return [relabel(f, dict(zip([x, y], ch['qmap'][i]))) for i, f in enumerate(base)]

def ng(ch):
    m, n, q, xx = ch['nglab']
    big = lambda t: no(eqt(t, mul(t, t)))
    pr = lambda t: an(big(t), al(m, al(n, im(eqt(t, mul(m, n)), orr(eqt(m, t), eqt(n, t))))))
    bad = no(al(xx, im(orr(eqt(xx, n), eqt(xx, q)), pr(xx))))
    return ex(m, ex(n, ands(eqt(m, add(n, n)), big(n), al(n, al(q, im(eqt(m, add(n, q)), bad))))))

def assemble(ch):
    EUC = im(eqt('c', 'a'), eqt('c', 'b'), eqt('a', 'b'))     # term Euclid (sym+trans)
    R1 = ex('a', eqt('a', 'b'))                               # ∃x x==y  (y a var term)
    rows = [P.L, EUC, P.B6C, P.COMM, P.QI, R1] + qaxioms(ch) + [ng(ch)]
    rows = [rows[i] for i in ch['rorder']]
    IND = im(al('a', im(eqt('a', 'Z'), PHI)),
             al('a', im(PHI, al('c', im(eqt('c', S('a')), al('a', im(eqt('a', 'c'), PHI)))))),
             al('a', PHI))
    LZ = im(eqt('a', 'c'), PHI, al('a', im(eqt('a', 'c'), PHI)))
    VAC = im(PHI, al('c', PHI))
    b = [IND, LZ, VAC]
    b = [b[i] for i in ch['border']]
    return [P.GEN], rows, ands(*b)

def default_choice():
    return {'qmap': [['a', 'b']] * 6, 'nglab': ['1', '0', '3', '2'],
            'rorder': list(range(13)), 'border': list(range(3))}

def random_choice(rng):
    return {'qmap': [rng.sample(LAB, 2) for _ in range(6)],
            'nglab': rng.sample(['0', '1', '2', '3'], 4),
            'rorder': rng.sample(range(13), 13), 'border': rng.sample(range(3), 3)}

def mutate(ch, rng):
    ch = json.loads(json.dumps(ch))
    k = rng.choice(['qmap', 'qmap', 'nglab', 'rorder', 'rorder', 'border'])
    if k == 'qmap': ch['qmap'][rng.randrange(6)] = rng.sample(LAB, 2)
    elif k in ('rorder', 'border'):
        o = ch[k]; i, j = rng.sample(range(len(o)), 2); o[i], o[j] = o[j], o[i]
    else: ch[k] = random_choice(rng)[k]
    return ch

def score(ch, name):
    pre, post, b = assemble(ch)
    return build(name, pre, post, b)[0]

if __name__ == '__main__':
    if os.name == 'nt':
        import ctypes
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
    seed, iters = int(sys.argv[1]), int(sys.argv[2])
    tag = sys.argv[3] if len(sys.argv) > 3 else 'n'
    rng = random.Random(seed)
    name = f'srchn_{tag}_{seed}'
    out = open(os.path.join(HERE, 'runs', f'search_nest_{tag}_{seed}.jsonl'), 'w')
    cur = default_choice() if seed == 0 else random_choice(rng)
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
    print('done', best[0], json.dumps(best[1]))
