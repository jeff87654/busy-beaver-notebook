"""Order/label search for the UG' bundle (interface change of 2026-10-14: ∀f after w, union container).

Variants
  A : clause 3 = H → ∃U∈w ∀y∈C ∀z∈y z∈U                    (interface text)
  B : clause 3 = H → C∈w, plus per-x union container ∃U∈w ∀t∈x ∀z∈t z∈U   (allowed equivalent)
Fixed labels (collision-safe core of the 288 design): w = d (c+1), x = B = b, C = W = c, z = d,
u1 = u2 = c, p = c, f = 0 (v_0, bound by ∀ right after w, outside the ∀x∈w), φ input a, output b.
The new roles (U and its element variables) range over a, b, c, d (capture-checked).

Usage: python search2.py <A|B> <nworkers> <worker> [alllabels]
"""
import sys, os, itertools, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen
gen.PUSH['0'] = ['v_0']

def sub(x, y, u): return ('all', u, ('im', ('el', u, x), ('el', u, y)))
def A(p, q, flip): return ('and', q, p) if flip else ('and', p, q)

def base(var, o):
    cl1 = ('all', 'in', ('im', ('el', 'in', 'x'), ('all', 'o1', ('im', ('phi', 'in', 'o1'),
           ('ex', 'o2', A(('phi', 'in', 'o2'), ('el', 'o2', 'C'), o['cl1f']))))))
    cl2 = ('all', 'o3', ('im', ('el', 'o3', 'C'), ('ex', 'i3', ('phi', 'i3', 'o3'))))
    H = ('all', 'i4', ('im', ('el', 'i4', 'x'), ('ex', 'o4', A(('el', 'o4', 'w'), ('phi', 'i4', 'o4'), o['hf']))))
    if var == 'A':
        concl = ('ex', 'U', A(('all', 'y5', ('im', ('el', 'y5', 'C'), sub('y5', 'U', 'z5'))), ('el', 'U', 'w'), o['uf']))
    else:
        concl = ('el', 'C', 'w')
    cl3 = ('im', H, concl)
    cls = [cl1, cl2, cl3]
    cs = [cls[i] for i in list(itertools.permutations(range(3)))[o['yperm']]]
    Yb = A(cs[0], A(cs[1], cs[2], False), False) if not o['yleft'] else A(A(cs[0], cs[1], False), cs[2], False)
    Y = ('ex', 'C', Yb)
    T = sub('x', 'w', 'u2')
    Q = ('ex', 'W', A(('all', 'z', ('im', sub('z', 'x', 'u1'), ('el', 'z', 'W'))), ('el', 'W', 'w'), o['qf']))
    if var == 'W':      # OPTIONAL EXTRA (not interface-equivalent): union bound inside Q's container W
        un = ('all', 't', ('im', ('el', 't', 'x'), sub('t', 'W', 'z6')))
        pw = ('all', 'z', ('im', sub('z', 'x', 'u1'), ('el', 'z', 'W')))
        Q = ('ex', 'W', A(A(pw, un, o['uf']), ('el', 'W', 'w'), o['qf']))
    xs = [Q, T]
    if var == 'B':
        UC = ('ex', 'U', A(('all', 't', ('im', ('el', 't', 'x'), sub('t', 'U', 'z6'))), ('el', 'U', 'w'), o['uf']))
        xs.append(UC)
    xs = [xs[i] for i in list(itertools.permutations(range(len(xs))))[o['xperm'] % len(xs)]]
    X = xs[0] if len(xs) == 1 else A(xs[0], xs[1] if len(xs) == 2 else A(xs[1], xs[2], False), False)
    body = ('all', 'f', ('all', 'x', ('im', ('el', 'x', 'w'), A(X, Y, o['xyf']))))
    return ('ex', 'w', A(('el', 'p', 'w'), body, o['pf']))

def order_keys(var):
    return {'cl1f': 2, 'hf': 2, 'yperm': 6, 'yleft': 2, 'qf': 2, 'xperm': 6 if var == 'B' else 2,
            'xyf': 2, 'pf': 2, 'uf': 2, 'vflip': 2}

FIXED = {'in': 'a', 'i3': 'a', 'i4': 'a', 'o1': 'b', 'o2': 'b', 'o3': 'b', 'o4': 'b',
         'w': 'd', 'x': 'b', 'C': 'c', 'W': 'c', 'z': 'd', 'u1': 'c', 'u2': 'c', 'p': 'c', 'f': '0'}

def check(g, lab, env=()):
    def look(l):
        for (k, r) in reversed(env):
            if k == l: return r
        return None
    h = g[0]
    if h in ('all', 'ex'): return check(g[2], lab, env + ((lab[g[1]], g[1]),))
    if h in ('im', 'and'): return check(g[1], lab, env) and check(g[2], lab, env)
    if h == 'el':
        for r in g[1:]:
            if r == 'p':
                if look(lab['p']) is not None: return False
            elif look(lab[r]) != r: return False
        return True
    if h == 'phi': return look('a') == g[1] and look('b') == g[2] and look('0') == 'f'
    raise ValueError(g)

def roles(g, acc):
    if g[0] in ('all', 'ex'): acc.append(g[1]); roles(g[2], acc)
    elif g[0] in ('im', 'and'): roles(g[1], acc); roles(g[2], acc)
    return acc

def render(g, lab):
    h = g[0]
    if h in ('all', 'ex'): return (h, lab[g[1]], render(g[2], lab))
    if h in ('im', 'and'): return (h, render(g[1], lab), render(g[2], lab))
    if h == 'el': return ('el', lab[g[1]], lab[g[2]])
    return 'phi'

def assignments(var, labels):
    o0 = {k: 0 for k in order_keys(var)}
    g = base(var, o0)
    free = [r for r in dict.fromkeys(roles(g, [])) if r not in FIXED]
    out = []
    for combo in itertools.product(labels, repeat=len(free)):
        lab = dict(FIXED); lab.update(zip(free, combo))
        if check(g, lab): out.append(lab)
    return out

def full(var, o, lab):
    Vf = gen.V()
    V2 = ('and', Vf[2], Vf[1]) if o['vflip'] else ('and', Vf[1], Vf[2])
    return ('and', render(base(var, o), lab), V2)

def main():
    if os.name == 'nt':
        import ctypes
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
    var, nw, wk = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    labels = ['a', 'b', 'c', 'd'] if len(sys.argv) > 4 else ['b', 'c', 'd']
    labs = assignments(var, labels)
    print('assignments', len(labs), [{k: v for k, v in l.items() if k not in FIXED} for l in labs], flush=True)
    ok = order_keys(var)
    name = f'srch2_{var}_{wk}'
    out = open(os.path.join(HERE, 'runs', f'search2_{var}_{wk}.jsonl'), 'w')
    best = None; i = 0
    for vals in itertools.product(*[range(n) for n in ok.values()]):
        for lab in labs:
            i += 1
            if i % nw != wk: continue
            o = dict(zip(ok, vals))
            f = full(var, o, lab)
            gen.gen_source(name, fn=lambda f=f: f)
            z, ns = gen.compile_variant(name)
            rec = {'states': ns, 'o': o, 'lab': {k: v for k, v in lab.items() if k not in FIXED}}
            out.write(json.dumps(rec) + '\n'); out.flush()
            if best is None or ns < best[0]:
                best = (ns, rec); print('best', ns, rec, flush=True)
    os.remove(os.path.join(HERE, f'source_{name}.py'))
    print('done; best', best)

if __name__ == '__main__':
    main()
