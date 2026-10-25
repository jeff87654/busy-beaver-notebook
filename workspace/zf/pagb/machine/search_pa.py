"""Random/local search over row order, conjunct order and label choices of the FLAT+Leibniz PA source.

Usage: python search_pa.py <seed> <iterations> [tag]
Writes runs/search_pa_<tag>_<seed>.jsonl (one record per improvement) and prints the best.
All choices are soundness-neutral (see DESIGN.md: open rows are closed under relabeling;
vacuity rows use labels from {a,b,d}, all distinct from c under the gate).
"""
import sys, os, json, random, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pagen import *
import pavars as P

LAB5 = ['a', 'b', 'c', 'd', '0']

def relabel(f, m):
    if isinstance(f, str):
        return m.get(f, f)
    if f[0] in ('S', 'add', 'mul', 'rel', 'eq', 'im', 'all', 'ex', 'and', 'or', 'not'):
        return (f[0],) + tuple(relabel(x, m) for x in f[1:])
    return f

def qaxioms(ch):
    """Q axioms with the generic names x,y,u,w,v relabeled by ch['qmap'][i] (a permutation of LAB5)."""
    x, y, u, w, v = 'x', 'y', 'u_', 'w', 'v'
    base = [
        im(rel(x, Z), no(rel(x, S(y)))),
        im(rel(u, S(x)), rel(u, S(y)), eq(x, y)),
        im(rel(x, Z), rel(y, add(x, y))),
        im(rel(u, S(x)), rel(w, add(x, y)), rel(v, S(w)), rel(v, add(u, y))),
        im(rel(x, Z), rel(x, mul(x, y))),
        im(rel(u, S(x)), rel(w, mul(x, y)), rel(v, add(y, w)), rel(v, mul(u, y))),
    ]
    out = []
    for i, f in enumerate(base):
        perm = ch['qmap'][i]
        out.append(relabel(f, dict(zip([x, y, u, w, v], perm))))
    return out

VAC = im(PHI, al('c', PHI))              # vacuous-quantifier schema: c (= the code) ∉ φ = decode(c)

def assemble(ch):
    fun = im(rel(ch['fun'][0], ch['fun'][2]), rel(ch['fun'][1], ch['fun'][2]), eq(ch['fun'][0], ch['fun'][1]))
    rows = [P.L, P.EUC, P.B6C, P.COMM, P.QI, P.R1, fun, P.EXd] + qaxioms(ch) + [P.ng2(*ch['nglab'])]
    rows = [rows[i] for i in ch['rorder']]
    b = [P.IND, P.LZ, VAC]
    b = [b[i] for i in ch['border']]
    return [P.GEN], rows, ands(*b)

def random_choice(rng):
    return {'qmap': [rng.sample(LAB5, 5) for _ in range(6)],
            'fun': rng.choice([('a', 'c', 'b'), ('a', 'b', 'c'), ('c', 'a', 'b'), ('b', 'a', 'c'),
                               ('b', 'c', 'a'), ('c', 'b', 'a')]),
            'nglab': rng.sample(['0', '1', '2', '3'], 4),
            'rorder': rng.sample(range(15), 15),
            'border': rng.sample(range(3), 3)}

def mutate(ch, rng):
    ch = json.loads(json.dumps(ch))
    k = rng.choice(['qmap', 'qmap', 'fun', 'nglab', 'rorder', 'rorder', 'border'])
    if k == 'qmap':
        ch['qmap'][rng.randrange(6)] = rng.sample(LAB5, 5)
    elif k in ('rorder', 'border'):
        o = ch[k]; i, j = rng.sample(range(len(o)), 2); o[i], o[j] = o[j], o[i]
    else:
        ch[k] = random_choice(rng)[k]
    return ch

def score(ch, name):
    pre, post, b = assemble(ch)
    ns, nt = build(name, pre, post, b)
    return ns

def default_choice():
    return {'qmap': [['a', 'b', 'c', 'd', '0']] * 6, 'fun': ('a', 'c', 'b'),
            'nglab': ['1', '0', '3', '2'], 'rorder': list(range(15)), 'border': list(range(3))}

if __name__ == '__main__':
    if os.name == 'nt':
        import ctypes
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
    seed, iters = int(sys.argv[1]), int(sys.argv[2])
    tag = sys.argv[3] if len(sys.argv) > 3 else 'a'
    rng = random.Random(seed)
    name = f'srch_{tag}_{seed}'
    out = open(os.path.join(HERE, 'runs', f'search_pa_{tag}_{seed}.jsonl'), 'w')
    cur = default_choice() if seed == 0 else random_choice(rng)
    cs = score(cur, name); best = (cs, cur)
    print('start', cs, flush=True)
    stall = 0
    for it in range(iters):
        nxt = mutate(cur, rng)
        ns = score(nxt, name)
        if ns <= cs:
            if ns < cs: stall = 0
            cur, cs = nxt, ns
        else:
            stall += 1
        if cs < best[0]:
            best = (cs, cur)
            out.write(json.dumps({'states': cs, 'it': it, 'ch': cur}) + '\n'); out.flush()
            print('best', cs, it, flush=True)
        if stall > 400:                        # restart from best with a big shake
            cur = best[1]
            for _ in range(5): cur = mutate(cur, rng)
            cs = score(cur, name); stall = 0
    out.write(json.dumps({'final': best[0], 'ch': best[1]}) + '\n')
    print('done', best[0], json.dumps(best[1]))
