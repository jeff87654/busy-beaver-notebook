"""Collision analysis for a labelled role formula (search.base).

For an identification of labels (a=b, d=a, d=b, d=a=b) re-resolve every variable occurrence and
report where it no longer reaches its intended binder.  A subtree guarded by ∀r(r∈s → ...) whose
guard now resolves to r∈r is vacuous by IR and is skipped (reported as 'vacuous').

Usage: python collide.py      (prints the analysis of the chosen assignment(s) in CANDIDATES)
"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import search

IDENTS = {'a=b': {'b': 'a'}, 'd=a': {'d': 'a'}, 'd=b': {'d': 'b'}, 'd=a=b': {'b': 'a', 'd': 'a'}}

def analyse(f, lab, ident):
    L = lambda r: ident.get(lab[r], lab[r])
    out = []
    def look(env, l):
        for (k, r) in reversed(env):
            if k == l: return r
        return None
    def res(env, r):
        return 'FREE' if look(env, L(r)) is None else look(env, L(r))
    def want(r):
        return 'FREE' if r == 'p' else r
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
                if res(env, r) != want(r):
                    out.append(('MISMATCH', path, f'{g[1]}∈{g[2]}: {r} -> {res(env, r)}'))
        elif h == 'phi':
            ra, rb = look(env, ident.get('a', 'a')), look(env, ident.get('b', 'b'))
            if (ra, rb) != (g[1], g[2]):
                out.append(('PHI', path, f'phi({g[1]},{g[2]}) -> phi({ra},{rb})'))
    walk(f, (), [])
    return out

def report(fam, o, lab):
    f = search.base(fam, o)
    for name, ident in IDENTS.items():
        print(' ', name)
        for kind, path, msg in analyse(f, lab, ident):
            print('    ', kind, '/'.join(path), msg)

if __name__ == '__main__':
    o0 = {k: 0 for k in search.ORDER_KEYS}
    search.FIXED['w'] = 'd'
    labs = list(search.assignments(search.base('ug0d', o0), ['a', 'b', 'c', 'd'], ['c']))
    del search.FIXED['w']
    print(len(labs), 'assignments')
    for lab in labs:
        print({k: v for k, v in lab.items() if k not in search.FIXED})
        report('ug0d', o0, lab)
