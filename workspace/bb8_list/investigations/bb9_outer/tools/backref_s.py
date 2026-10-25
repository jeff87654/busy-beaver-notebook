"""backref.py: backward-reasoning check of whether an undefined slot (Q,s) can ever be read.
A hypothesis = (state, dict pos->symbol) relative to the current head (pos 0 = scanned cell).
Step back over every transition X,x -> w,d,Q: previous head at -d; the cell at -d now holds w (must agree with
any constraint there), before it held x.  Constraints are shifted so the previous head is pos 0.
If every branch dies within DEPTH steps, the slot is unreachable (sound: a real path would give a surviving branch).
Branches that reach depth DEPTH, or reach the start (state A on a blank-compatible window), are 'possible'.
  python backref.py MACHINE [DEPTH]   (prints each undefined slot: UNREACHABLE (depth) / POSSIBLE)"""
import sys
def parse(m):
    rows = m.split('_'); T = {}
    for q, r in enumerate(rows):
        for c in (0, 1):
            x = r[3*c:3*c+3]
            T[(q, c)] = None if ('-' in x or x[2] == 'Z') else (int(x[0]), 1 if x[1] == 'R' else -1, ord(x[2]) - 65)
    return len(rows), T
def check(m, depth=40, maxnodes=200000, start=0):
    n, T = parse(m)
    preds = {}
    for (q, c), v in T.items():
        if v: preds.setdefault(v[2], []).append((q, c, v[0], v[1]))
    out = []
    for (q, s), v in T.items():
        if v is not None: continue
        frontier = [(q, ((0, s),))]; seen = set(); nodes = 0; possible = False; d = 0
        for d in range(depth):
            nxt = []
            for st, cons in frontier:
                cd = dict(cons)
                # start configuration: state `start`, all constrained cells blank, step 0
                if st == start and all(v == 0 for v in cd.values()): possible = True; break
                for (X, x, w, dd, ) in preds.get(st, []):
                    # previous head at -dd relative to current head
                    p = -dd
                    if cd.get(p, w) != w: continue
                    nd = {k + dd: v for k, v in cd.items() if k != p}   # shift: previous head becomes 0
                    nd[0] = x
                    key = (X, tuple(sorted(nd.items())))
                    if key in seen: continue
                    seen.add(key); nxt.append(key); nodes += 1
            if possible or not nxt: break
            if nodes > maxnodes: possible = None; break
            frontier = nxt
        if possible: out.append(('%s%d' % (chr(65+q), s), 'POSSIBLE'))
        elif possible is None or nxt: out.append(('%s%d' % (chr(65+q), s), 'UNDECIDED(depth %d)' % (d+1)))
        else: out.append(('%s%d' % (chr(65+q), s), 'UNREACHABLE (dies at depth %d)' % (d+1)))
    return out
if __name__ == '__main__' and sys.argv[1] == '--list':
    dep = int(sys.argv[3]) if len(sys.argv) > 3 else 40
    for ln in open(sys.argv[2]):
        f = ln.split()
        if len(f) < 2: continue
        print(f[0], f[1], check(f[0], dep, start=ord(f[1]) - 65), flush=True)
elif __name__ == '__main__':
    st = ord(sys.argv[3]) - 65 if len(sys.argv) > 3 else 0
    print(sys.argv[1], check(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 40, start=st))
# batch mode (bb9_f1 addition): python backref_s.py --list FILE [DEPTH]; FILE lines "MACHINE START ..."
if __name__ == '__main__' and False: pass
