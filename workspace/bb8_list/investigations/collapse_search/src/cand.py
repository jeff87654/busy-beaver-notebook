"""cand.py: collapse-candidate generator (n -> n-1 states) for 2-symbol TMs.
Families (kept states keep their relative order; the start state A is never deleted):
  D  X       delete X; every transition (S,c)->X from a kept state S is replaced by any (w,d,T), T kept, or halt.
  DR X Y     delete X; every incoming transition is retargeted to Y with any (w,d); Y's two slots are each
             'unchanged' or any of the 4(n-1)+1 options (Y absorbs X's role).  Only if in(X) <= 3.
  M  X Y     merge X,Y into one state Z (refs to X,Y -> Z); slot c taken from X_c or Y_c (both mapped), or,
             for at most one slot, any of the 4(n-1)+1 options.
A candidate must contain at least one halt slot.  Output lines: MACHINE TAG MAP  (MAP = for each parent state its
candidate index, or '.', e.g. 01234567. for 'I deleted').
usage: python cand.py PARENT [--fam D,DR,M] [--only X] > file"""
import sys, itertools
def parse(m):
    T = []
    for row in m.split('_'):
        r = []
        for c in range(2):
            t = row[3*c:3*c+3]
            r.append(None if t[0] == '-' or t[2] == 'Z' else (int(t[0]), t[1], ord(t[2]) - 65))
        T.append(r)
    return T
def fmt(T):
    return '_'.join(''.join('---' if t is None else '%d%s%s' % (t[0], t[1], chr(65 + t[2])) for t in r) for r in T)
def build(P, kept, slotfun):
    """slotfun(s,c) -> transition in PARENT index space (target may be any parent state in kept) or None"""
    ren = {o: i for i, o in enumerate(kept)}
    T = []
    for s in kept:
        r = []
        for c in range(2):
            t = slotfun(s, c)
            r.append(None if t is None else (t[0], t[1], ren[t[2]]))
        T.append(r)
    return T, ''.join(str(ren[s]) if s in ren else '.' for s in range(len(P)))
def main():
    P = parse(sys.argv[1]); n = len(P)
    fams = 'D,DR,M'.split(',')
    only = None
    a = sys.argv[2:]
    for i in range(len(a)):
        if a[i] == '--fam': fams = a[i+1].split(',')
        if a[i] == '--only': only = ord(a[i+1]) - 65
    seen = set(); out = sys.stdout
    def emit(T, tag, mp):
        if not any(t is None for r in T for t in r): return
        m = fmt(T)
        if m in seen: return
        seen.add(m); out.write('%s %s %s\n' % (m, tag, mp))
    for X in range(1, n):
        if only is not None and X != only: continue
        kept = [s for s in range(n) if s != X]
        opts = [None] + [(w, d, T) for T in kept for w in (0, 1) for d in 'LR']
        inc = [(s, c) for s in kept for c in range(2) if P[s][c] is not None and P[s][c][2] == X]
        if 'D' in fams:
            for ch in itertools.product(range(len(opts)), repeat=len(inc)):
                rep = {inc[i]: opts[ch[i]] for i in range(len(inc))}
                T, mp = build(P, kept, lambda s, c: rep[(s, c)] if (s, c) in rep else P[s][c])
                emit(T, 'D%s:%s' % (chr(65+X), ','.join(map(str, ch))), mp)
        if 'DR' in fams and len(inc) <= 3:
            for Y in kept:
                for wd in itertools.product([(w, d) for w in (0, 1) for d in 'LR'], repeat=len(inc)):
                    rep = {inc[i]: (wd[i][0], wd[i][1], Y) for i in range(len(inc))}
                    for y0 in range(len(opts) + 1):
                        for y1 in range(len(opts) + 1):
                            def sf(s, c):
                                if s == Y:
                                    k = y0 if c == 0 else y1
                                    if k == len(opts):
                                        t = rep.get((s, c), P[s][c])
                                        return t if t is None or t[2] != X else (t[0], t[1], Y)
                                    return opts[k]
                                return rep[(s, c)] if (s, c) in rep else P[s][c]
                            T, mp = build(P, kept, sf)
                            emit(T, 'DR%s%s:%d,%d' % (chr(65+X), chr(65+Y), y0, y1), mp)
    if 'M' in fams:
        for X in range(1, n):
            for Y in range(0, X):
                if only is not None and only not in (X, Y): continue
                kept = [s for s in range(n) if s != X]
                opts = [None] + [(w, d, T) for T in kept for w in (0, 1) for d in 'LR']
                mp_ = lambda t: t if t is None or t[2] != X else (t[0], t[1], Y)
                base = {}
                for c in range(2):
                    base[c] = [mp_(P[X][c]), mp_(P[Y][c])]
                for c0 in range(2 + len(opts)):
                    for c1 in range(2 + len(opts)):
                        if c0 >= 2 and c1 >= 2: continue
                        z0 = base[0][c0] if c0 < 2 else opts[c0 - 2]
                        z1 = base[1][c1] if c1 < 2 else opts[c1 - 2]
                        def sf(s, c):
                            if s == Y: return z0 if c == 0 else z1
                            return mp_(P[s][c])
                        T, m2 = build(P, kept, sf)
                        mp = ''.join(m2[s] if s != X else m2[Y] for s in range(n))
                        emit(T, 'M%s%s:%d,%d' % (chr(65+X), chr(65+Y), c0, c1), mp)
main()
