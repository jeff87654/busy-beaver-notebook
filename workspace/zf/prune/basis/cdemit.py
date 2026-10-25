"""zf/prune copy of zf/tools/cdsearch.py: axioms and the provability predicate are configurable.
Condensed-detachment search in Lukasiewicz's system CCpqCCqrCpr, CCNppp, CpCNpq
(the propositional part B1 B2 B3 of the ZF machine's Hilbert system).  Finds derivations of
target theses and emits Coq lemmas (prov-instances, explicit DET terms) for coq/L1_Prop.v.
Usage: python tools/cdsearch.py > coq/L1_Prop_gen.txt"""
import sys, heapq, itertools

# terms: int (var) | ('C', a, b) | ('N', a)
def parse(s):
    pos = 0
    def go():
        nonlocal pos
        c = s[pos]; pos += 1
        if c == 'C':
            a = go(); b = go(); return ('C', a, b)
        if c == 'N':
            return ('N', go())
        return 'pqrstuvw'.index(c)
    t = go(); assert pos == len(s); return t

def show(t):
    if isinstance(t, int): return 'pqrstuvwxyzabcdefghijklmno'[t] if t < 26 else f'v{t}'
    if t[0] == 'C': return 'C' + show(t[1]) + show(t[2])
    return 'N' + show(t[1])

def size(t):
    if isinstance(t, int): return 1
    return 1 + sum(size(x) for x in t[1:])

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

def shift(t, k):
    if isinstance(t, int): return t + k
    return (t[0],) + tuple(shift(x, k) for x in t[1:])

def canon(t):
    m = {}
    def go(t):
        if isinstance(t, int):
            if t not in m: m[t] = len(m)
            return m[t]
        return (t[0],) + tuple(go(x) for x in t[1:])
    return go(t), m

def match(pat, t, s):
    """one-way: instantiate vars of pat to make t"""
    if isinstance(pat, int):
        if pat in s: return s if s[pat] == t else None
        s = dict(s); s[pat] = t; return s
    if isinstance(t, int) or pat[0] != t[0]: return None
    for x, y in zip(pat[1:], t[1:]):
        s = match(x, y, s)
        if s is None: return None
    return s

def nvars(t):
    if isinstance(t, int): return t + 1
    return max(nvars(x) for x in t[1:])

AX = [('B1', parse('CCpqCCqrCpr')), ('B2', parse('CCNppp')), ('B3', parse('CpCNpq'))]
PROV = 'prov'
PFX = 'lp'

def search(targets, maxsize=23, maxgiven=20000):
    thm = []      # (formula, origin)  origin = ('ax', name) | ('cd', i, j)
    seen = set()
    sos = []
    cnt = itertools.count()
    def add(f, org):
        f, _ = canon(f)
        if f in seen or size(f) > maxsize: return
        seen.add(f)
        heapq.heappush(sos, (size(f), next(cnt), f, org))
    for n, f in AX: add(f, ('ax', n))
    found = {}
    usable = []
    given = 0
    while sos and given < maxgiven:
        _, _, f, org = heapq.heappop(sos)
        # forward subsumption by usable
        if any(match(u, f, {}) is not None for u in [thm[i][0] for i in usable]):
            continue
        idx = len(thm); thm.append((f, org)); usable.append(idx); given += 1
        for t in targets:
            if t not in found and match(f, parse(t), {}) is not None:
                found[t] = idx
                print(f'# found {t} via #{idx} {show(f)} given={given}', file=sys.stderr)
        if len(found) == len(targets): break
        for j in list(usable):
            for (ma, mi) in ((idx, j), (j, idx)):
                M = thm[ma][0]; m = thm[mi][0]
                if isinstance(M, int) or M[0] != 'C': continue
                k = nvars(M)
                s = unify(M[1], shift(m, k), {})
                if s is None: continue
                add(subst(M[2], s), ('cd', ma, mi))
    return thm, found

if __name__ == '__main__':
    targets = sys.argv[1:] or ['Cpp', 'CpCqp', 'CCpCpqCpq', 'CCpqCNqNp', 'CNCpNqp', 'CNNpp', 'CpNNp']
    thm, found = search(targets)
    for t in targets:
        print(t, 'FOUND' if t in found else 'missing', file=sys.stderr)


def coq_term(t, names):
    if isinstance(t, int): return names(t)
    if t[0] == 'C': return f'(Wim {coq_term(t[1], names)} {coq_term(t[2], names)})'
    return f'(Wn {coq_term(t[1], names)})'

def emit_coq(thm, found, targets, tnames):
    need = set()
    def mark(i):
        if i in need: return
        need.add(i)
        org = thm[i][1]
        if org[0] == 'cd': mark(org[1]); mark(org[2])
    for t in targets: mark(found[t])
    nm = lambda i: thm[i][1][1] if thm[i][1][0] == 'ax' else f'{PFX}{i}'
    out = []
    for i in sorted(need):
        f, org = thm[i]
        if org[0] == 'ax': continue
        _, ma, mi = org
        M = thm[ma][0]; m = thm[mi][0]; k = nvars(M)
        s = unify(M[1], shift(m, k), {})
        R = subst(M[2], s)
        Rc, ren = canon(R)
        assert Rc == f
        n = nvars(f) if not isinstance(f, int) else f + 1
        vn = lambda v: f'w{v}'
        def inst(t):
            t = subst(t, s)
            def nm2(v):
                return f'w{ren[v]}' if v in ren else '(Weq 0 0)'
            return coq_term(t, nm2)
        maj_args = ' '.join(inst(v) for v in range(k))
        mi_args = ' '.join(inst(v + k) for v in range(nvars(m)))
        binders = ' '.join(f'w{v}' for v in range(n))
        out.append(f'Lemma {PFX}{i} ({binders} : wff) : {PROV} {coq_term(f, vn)}.\n'
                   f'Proof. exact (DET _ _ ({nm(ma)} {maj_args}) ({nm(mi)} {mi_args})). Qed.')
    for t, tn in zip(targets, tnames):
        i = found[t]; f = thm[i][0]; tt = parse(t)
        s = match(f, tt, {})
        n = nvars(tt)
        args = ' '.join(coq_term(s.get(v, ('C', 0, 0)), lambda v: f'w{v}') for v in range(nvars(f)))
        binders = ' '.join(f'w{v}' for v in range(n))
        out.append(f'Lemma {tn} ({binders} : wff) : {PROV} {coq_term(tt, lambda v: f"w{v}")}.\n'
                   f'Proof. exact ({nm(i)} {args}). Qed.')
    return '\n'.join(out)
