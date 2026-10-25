"""collapse.py: static 'pure mover' gadget elimination.
A state G (not the start state) with G0 = 0dY and G1 = 1dY (same direction d, same target Y != G) only steps back.
If every transition entering G moves in direction -d, then G always returns to the cell just written (value w) in
state Y, so each entry (S,c) -> (w,-d,G) equals one step (S,c) -> Y[w] (Y's transition on w; undefined -> undefined).
G is then unreachable and removed; states are renamed in order.  The reduced machine halts iff the original halts,
with the same final tape (a halt inside the gadget is impossible: Y[w] undefined is copied as undefined).
usage: python collapse.py FILE_OR_MACHINE...   prints  original -> reduced (states n -> n')  for each collapse."""
import sys, os
def parse(m):
    T = []
    for p in m.split('_'):
        row = []
        for c in range(2):
            t = p[3 * c:3 * c + 3]
            if t[0] == '-' or t[2] in 'Z-' or ord(t[2]) - 65 >= len(m.split('_')): row.append(None)
            else: row.append((int(t[0]), t[1], ord(t[2]) - 65))
        T.append(row)
    return T
def fmt(T):
    return '_'.join(''.join('---' if t is None else '%d%s%s' % (t[0], t[1], chr(65 + t[2])) for t in row) for row in T)
def step(T):
    n = len(T)
    for g in range(1, n):
        a, b = T[g]
        if a is None or b is None or a[0] != 0 or b[0] != 1 or a[1] != b[1] or a[2] != b[2] or a[2] == g: continue
        d, y = a[1], a[2]
        ent = [(s, c) for s in range(n) for c in range(2) if T[s][c] is not None and T[s][c][2] == g]
        if not ent or any(T[s][c][1] == d for s, c in ent): continue
        U = [list(r) for r in T]
        for s, c in ent: U[s][c] = T[y][T[s][c][0]]
        if any(U[s][c] is not None and U[s][c][2] == g for s, c in ent): continue   # Y[w] re-enters G: skip
        # drop g, rename
        keep = [i for i in range(n) if i != g]; ren = {o: i for i, o in enumerate(keep)}
        V = [[None if t is None else (t[0], t[1], ren[t[2]]) for t in U[o]] for o in keep]
        return V, g
    return None, None
def collapse(m):
    T = parse(m); hist = []
    while True:
        V, g = step(T)
        if V is None: return T, hist
        hist.append(chr(65 + g)); T = V
args = sys.argv[1:]
ms = []
for a in args:
    if os.path.exists(a): ms += [l.split()[0] for l in open(a) if l.strip() and not l.startswith('#')]
    else: ms.append(a)
for m in ms:
    T, h = collapse(m)
    if h: print('%s -> %s  (%d -> %d states, removed %s)' % (m, fmt(T), m.count('_') + 1, len(T), ','.join(h)))
