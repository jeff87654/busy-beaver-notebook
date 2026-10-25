"""Search equivalent renderings of the universe bundle for the smallest Wade compilation.

A bundle is written over ROLES (one role per binder, 'p' free).  A rendering picks
  * a label (a, b, c or the fresh code e) for every role, checked capture-free: every occurrence of
    a role must resolve to its own binder, the free point p must not be captured, and at each φ
    the innermost a-binder / b-binder must be the intended input / output;
  * an order for every commutable conjunction.
Each distinct RPN is compiled with Wade's TMBuilder (gen.compile_variant).

Usage: python search.py <family> <nsamples> [seed]     family: ug1 (C⊆w → C∈w) | ug0 (interface)
"""
import sys, os, random, itertools, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen

# ---- role formulas: ('all'|'ex', role, body) ('el', r, s) ('phi', rin, rout) ('im'|'and', A, B)
def sub(x, y, u): return ('all', u, ('im', ('el', u, x), ('el', u, y)))

def base(family, o):
    """o: dict of order switches (bool)."""
    def A(p, q, flip): return ('and', q, p) if flip else ('and', p, q)
    def phi_and(r_out, C, flip): return A(('phi', 'in', r_out), ('el', r_out, C), flip)
    cl1 = ('all', 'in', ('im', ('el', 'in', 'x'), ('all', 'o1', ('im', ('phi', 'in', 'o1'),
           ('ex', 'o2', phi_and('o2', 'C', o['cl1f']))))))
    cl2 = ('all', 'o3', ('im', ('el', 'o3', 'C'), ('ex', 'i3', ('phi', 'i3', 'o3'))))
    if family == 'ug1':           # REJECTED: too weak (a witness C with junk outside w makes it vacuous)
        cl3 = ('im', sub('C', 'w', 'u3'), ('el', 'C', 'w'))
    else:
        cl3 = ('im', ('all', 'i4', ('im', ('el', 'i4', 'x'), ('ex', 'o4', A(('el', 'o4', 'w'), ('phi', 'i4', 'o4'), o['hf'])))),
               ('el', 'C', 'w'))
    cls = [cl1, cl2, cl3]
    perm = list(itertools.permutations(range(3)))[o['yperm']]
    cs = [cls[i] for i in perm]
    Yb = A(cs[0], A(cs[1], cs[2], False), False) if not o['yleft'] else A(A(cs[0], cs[1], False), cs[2], False)
    Y = ('ex', 'C', Yb)
    T = sub('x', 'w', 'u2')
    Q = ('ex', 'W', A(('all', 'z', ('im', sub('z', 'x', 'u1'), ('el', 'z', 'W'))), ('el', 'W', 'w'), o['qf']))
    X = A(T, Q, o['xf'])
    body = ('all', 'x', ('im', ('el', 'x', 'w'), A(X, Y, o['xyf'])))
    return ('ex', 'w', A(('el', 'p', 'w'), body, o['pf']))

ORDER_KEYS = {'cl1f': 2, 'hf': 2, 'yperm': 6, 'yleft': 2, 'qf': 2, 'xf': 2, 'xyf': 2, 'pf': 2}

def roles_of(f, acc=None):
    acc = [] if acc is None else acc
    if f[0] in ('all', 'ex'):
        acc.append(f[1]); roles_of(f[2], acc)
    elif f[0] in ('im', 'and'):
        roles_of(f[1], acc); roles_of(f[2], acc)
    return acc

def check(f, lab, env=()):
    """capture check; env: tuple of (label, role), innermost last."""
    def look(l):
        for (k, r) in reversed(env):
            if k == l: return r
        return None
    h = f[0]
    if h in ('all', 'ex'):
        return check(f[2], lab, env + ((lab[f[1]], f[1]),))
    if h in ('im', 'and'):
        return check(f[1], lab, env) and check(f[2], lab, env)
    if h == 'el':
        for r in f[1:]:
            if r == 'p':
                if look(lab['p']) is not None: return False
            elif look(lab[r]) != r: return False
        return True
    if h == 'phi':
        return look('a') == f[1] and look('b') == f[2]
    raise ValueError(f)

def render(f, lab):
    h = f[0]
    if h in ('all', 'ex'): return (h, lab[f[1]], render(f[2], lab))
    if h == 'im': return ('im', render(f[1], lab), render(f[2], lab))
    if h == 'and': return ('and', render(f[1], lab), render(f[2], lab))
    if h == 'el': return ('el', lab[f[1]], lab[f[2]])
    if h == 'phi': return 'phi'

FIXED = {'in': 'a', 'i3': 'a', 'i4': 'a', 'o1': 'b', 'o2': 'b', 'o3': 'b', 'o4': 'b'}

def assignments(f, labels, plabels):
    free = [r for r in dict.fromkeys(roles_of(f)) if r not in FIXED]
    for combo in itertools.product(labels, repeat=len(free)):
        lab = dict(FIXED); lab.update(zip(free, combo))
        for pl in plabels:
            lab['p'] = pl
            if check(f, lab):
                yield dict(lab)

def full(fam, o, lab, vflip):
    ug = render(base(fam, o), lab)
    Vf = gen.V() if not vflip else ('and', gen.V()[2], gen.V()[1])
    return ('and', ug, Vf)

def idle():
    if os.name == 'nt':
        import ctypes
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)

def main():
    idle()
    fam = sys.argv[1]; nsamp = int(sys.argv[2]); seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    rnd = random.Random(seed)
    labels = ['a', 'b', 'c'] if fam in ('ug1', 'ug0d') else ['a', 'b', 'c', 'e']
    o0 = {k: 0 for k in ORDER_KEYS}
    if fam == 'ug0d':       # w = c+1 (only w), every other role in a, b, c
        FIXED['w'] = 'd'
        labs = list(assignments(base(fam, o0), labels, ['c']))      # p = c: never collides with w
        del FIXED['w']
    else:
        labs = list(assignments(base(fam, o0), labels, ['a', 'b', 'c']))
    if fam == 'ug0dz':      # the collision-safe assignment (see collide.py): 'a' only as the φ input
        fam = 'ug0d'
        labs = [dict(FIXED, w='d', x='b', u2='c', W='c', z='d', u1='c', C='c', p='c')]
    if fam == 'ug0':        # the interface needs the fresh label on w or C
        labs = [l for l in labs if 'e' in (l['w'], l['C'])]
    print('valid label assignments:', len(labs))
    seen = {}; best = None
    out = open(os.path.join(HERE, f'search_{fam}_{seed}.jsonl'), 'w')
    if nsamp > 0:
        def cands():
            for t in range(nsamp):
                yield ({k: rnd.randrange(n) for k, n in ORDER_KEYS.items()}, rnd.choice(labs), rnd.randrange(2))
    else:                   # exhaustive, split over workers: argv[3] = worker index, argv[4] = nworkers
        nw = int(sys.argv[4]) if len(sys.argv) > 4 else 1
        def cands():
            i = 0
            for vals in itertools.product(*[range(n) for n in ORDER_KEYS.values()]):
                for lab in labs:
                    for vflip in range(2):
                        if i % nw == seed % nw:
                            yield (dict(zip(ORDER_KEYS, vals)), lab, vflip)
                        i += 1
    for (o, lab, vflip) in cands():
        if not check(base(fam, o), lab):
            continue
        f = full(fam, o, lab, vflip)
        key = tuple(gen.rpn(f))
        if key in seen: continue
        name = f'srch_{fam}_{seed}'
        gen.gen_source(name, fn=lambda f=f: f)
        z, ns = gen.compile_variant(name)
        seen[key] = ns
        rec = {'states': ns, 'o': o, 'lab': lab, 'vflip': vflip, 'ntok': len(key)}
        out.write(json.dumps(rec) + '\n'); out.flush()
        if best is None or ns < best[0]:
            best = (ns, rec); print('best', ns, rec, flush=True)
    os.remove(os.path.join(HERE, f'source_srch_{fam}_{seed}.py'))
    print('done', len(seen), 'distinct; best', best)

if __name__ == '__main__':
    main()
