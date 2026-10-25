"""Collision analysis for the UG' bundle (search2.base): every identification of the labels
a, b, c, d (= c+1) and 0 (= f) that the gate leaves open (c ∉ {a,b}; d ≠ c, d ≠ 0 always).

For each identification every variable occurrence is re-resolved.  Reported:
  vacuous   ∀r(r∈s → …) whose guard now resolves to r∈r (true by IR; subtree skipped)
  MISMATCH  an atom argument that now reaches another binder
  PHI       a φ occurrence whose input / output / f now reach other binders
Usage: python collide2.py <A|B> [json-order]      (default order: all switches 0)
"""
import sys, os, json, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import search2

LABELS = ['a', 'b', 'c', 'd', '0']

def partitions(xs):
    if not xs:
        yield []; return
    x, rest = xs[0], xs[1:]
    for p in partitions(rest):
        for i in range(len(p)):
            yield p[:i] + [[x] + p[i]] + p[i + 1:]
        yield [[x]] + p

def allowed(p):
    cls = {l: i for i, blk in enumerate(p) for l in blk}
    return not (cls['c'] in (cls['a'], cls['b']) or cls['d'] in (cls['c'], cls['0']))

def analyse(g, lab, ident):
    L = lambda r: ident.get(lab[r], lab[r])
    out = []
    def look(env, l):
        for (k, r) in reversed(env):
            if k == l: return r
        return None
    def res(env, r):
        return look(env, L(r)) or 'FREE'
    def walk(g, env, path):
        h = g[0]
        if h in ('all', 'ex'):
            env2 = env + ((L(g[1]), g[1]),)
            body = g[2]
            if h == 'all' and body[0] == 'im' and body[1][0] == 'el':
                r, s = body[1][1], body[1][2]
                if res(env2, r) == res(env2, s):
                    out.append(('vacuous', path + [h + g[1]], f'{r}∈{s} -> {res(env2, r)}∈{res(env2, s)}'))
                    return
            walk(body, env2, path + [h + g[1]])
        elif h in ('im', 'and'):
            walk(g[1], env, path + [h + '1']); walk(g[2], env, path + [h + '2'])
        elif h == 'el':
            for r in g[1:]:
                want = 'FREE' if r == 'p' else r
                if res(env, r) != want:
                    out.append(('MISMATCH', path, f'{g[1]}∈{g[2]}: {r} -> {res(env, r)}'))
        elif h == 'phi':
            got = tuple(look(env, ident.get(l, l)) for l in ('a', 'b', '0'))
            if got != (g[1], g[2], 'f'):
                out.append(('PHI', path, f'phi(in,out,f)=({g[1]},{g[2]},f) -> {got}'))
    walk(g, (), [])
    return out

if __name__ == '__main__':
    var = sys.argv[1]
    o = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {k: 0 for k in search2.order_keys(var)}
    lab = search2.assignments(var, ['b', 'c', 'd'])[0]
    g = search2.base(var, o)
    for p in partitions(LABELS):
        if not allowed(p) or all(len(b) == 1 for b in p):
            continue
        ident = {l: blk[0] for blk in p for l in blk}
        name = ' '.join('='.join(b) for b in p if len(b) > 1)
        print(name)
        for kind, path, msg in analyse(g, lab, ident):
            print('    ', kind, '/'.join(path), msg)
