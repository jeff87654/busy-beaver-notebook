"""n-gram closed position set: abstract (q, l, r), l = n cells left of head (nearest last), r = n cells from head.
G = allowed (n+1)-grams. Iterate to fixpoint; if no halting config -> certificate."""
import sys, time
from sim1 import T
n = int(sys.argv[1]); maxcfg = int(sys.argv[2]) if len(sys.argv) > 2 else 3_000_000
def grams(s, k):
    return {s[i:i+k] for i in range(len(s)-k+1)}
Z = '0'*n
G = set()
seen = set()
work = []
def add_grams_of(win):
    new = False
    for g in grams(win, n+1):
        if g not in G:
            G.add(g); new = True
    return new
G.add('0'*(n+1))
init = (0, Z, Z)
seen.add(init); work.append(init)
# configs depend on G when extending; recompute with fixpoint loops
t0 = time.time()
changed = True
rounds = 0
halted = None
succ_cache = {}
while changed:
    changed = False
    rounds += 1
    i = 0
    work = list(seen)
    for (q, l, r) in work:
        # window gram update
        if add_grams_of(l + r): changed = True
        c = int(r[0])
        tr = T[(q, c)]
        if tr is None:
            halted = (q, l, r); continue
        w, d, q2 = tr
        r2 = str(w) + r[1:]
        if add_grams_of(l + r2): changed = True
        if d == 'R':
            # head moves to r[1], new left l[1:]+w, new right r[1:]+x
            l2 = l[1:] + str(w)
            for x in '01':
                if (r + x) in G or True:
                    pass
            for x in '01':
                if (r + x) in G:
                    nr = (q2, l2, r[1:] + x)
                    if nr not in seen:
                        seen.add(nr); changed = True
        else:
            # head moves left: new head cell = l[-1]; new right = l[-1] + w + r[1:][:n-2]... r2 = w + r[1:], new right window = l[-1] + r2[:n-1]
            for y in '01':
                if (y + l) in G:
                    nl = y + l[:-1]
                    nrr = l[-1] + r2[:n-1]
                    nr = (q2, nl, nrr)
                    if nr not in seen:
                        seen.add(nr); changed = True
    print('round', rounds, 'configs', len(seen), 'grams', len(G), 'halt' if halted else '', '%.0fs' % (time.time()-t0), flush=True)
    if halted or len(seen) > maxcfg:
        break
print('RESULT n=%d: %s' % (n, 'HALT-REACHED(no cert)' if halted else ('TOO BIG' if len(seen) > maxcfg else 'CLOSED: certificate')))
