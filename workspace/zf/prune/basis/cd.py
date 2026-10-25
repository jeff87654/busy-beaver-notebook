"""Condensed detachment saturation: does a set of C/N axiom schemes derive given targets (up to instance)?
Terms: int var | ('C',a,b) | ('N',a).  Given-clause loop with a size bound."""
import sys
sys.path.insert(0, '..')
def parse(s):
    pos = 0
    def go():
        nonlocal pos
        c = s[pos]; pos += 1
        if c == 'C': a = go(); b = go(); return ('C', a, b)
        if c == 'N': return ('N', go())
        return 'pqrstuvw'.index(c)
    t = go(); assert pos == len(s); return t
def show(t):
    if isinstance(t, int): return 'pqrstuvwxyzabcdefghijklmno'[t] if t < 26 else f'v{t}'
    return t[0] + ''.join(show(x) for x in t[1:])
def size(t): return 1 if isinstance(t, int) else 1 + sum(size(x) for x in t[1:])
def walk(t, s):
    while isinstance(t, int) and t in s: t = s[t]
    return t
def occurs(v, t, s):
    t = walk(t, s)
    if isinstance(t, int): return t == v
    return any(occurs(v, x, s) for x in t[1:])
def unify(a, b, s):
    a = walk(a, s); b = walk(b, s)
    if isinstance(a, int):
        if a == b: return s
        if occurs(a, b, s): return None
        s = dict(s); s[a] = b; return s
    if isinstance(b, int): return unify(b, a, s)
    if a[0] != b[0]: return None
    for x, y in zip(a[1:], b[1:]):
        s = unify(x, y, s)
        if s is None: return None
    return s
def subst(t, s):
    t = walk(t, s)
    if isinstance(t, int): return t
    return (t[0],) + tuple(subst(x, s) for x in t[1:])
def shift(t, k): return t + k if isinstance(t, int) else (t[0],) + tuple(shift(x, k) for x in t[1:])
def canon(t):
    m = {}
    def go(t):
        if isinstance(t, int):
            if t not in m: m[t] = len(m)
            return m[t]
        return (t[0],) + tuple(go(x) for x in t[1:])
    return go(t)
def match(p, t, s):
    """one-way: instance t of pattern p"""
    if isinstance(p, int):
        if p in s: return s if s[p] == t else None
        s = dict(s); s[p] = t; return s
    if isinstance(t, int) or p[0] != t[0]: return None
    for x, y in zip(p[1:], t[1:]):
        s = match(x, y, s)
        if s is None: return None
    return s
def subsumed(t, kept):
    return any(match(k, t, {}) is not None for k in kept)
def cd(major, minor):
    if isinstance(major, int) or major[0] != 'C': return None
    m2 = shift(minor, 100)
    s = unify(major[1], m2, {})
    if s is None: return None
    return canon(subst(major[2], s))
def derives(axioms, targets, maxsize=21, maxkept=1500, verbose=False):
    import heapq, itertools
    cnt = itertools.count()
    kept = []; heap = []
    for a in axioms: heapq.heappush(heap, (size(canon(a)), next(cnt), canon(a)))
    todo = [canon(t) for t in targets]; seen = set()
    while heap and len(kept) < maxkept:
        _, _, g = heapq.heappop(heap)
        if g in seen or subsumed(g, kept): continue
        seen.add(g); kept.append(g)
        todo = [t for t in todo if match(g, t, {}) is None]
        if not todo: return True, len(kept)
        for k in kept:
            for a, b in ((g, k), (k, g)):
                r = cd(a, b)
                if r is not None and size(r) <= maxsize and r not in seen:
                    heapq.heappush(heap, (size(r), next(cnt), r))
    return False, len(kept)
B1, B2, B3 = parse('CCpqCCqrCpr'), parse('CCNppp'), parse('CpCNpq')
if __name__ == '__main__':
    import time; t=time.time(); print(derives([B1, B2, B3], [parse('Cpp'), parse('CNNpp'), parse('CpNNp')]), time.time()-t)
