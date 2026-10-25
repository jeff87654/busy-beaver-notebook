"""round recorder for the exhausted-transit cascade.  From [6,6,3,60,T,0,1^w | A]: logs every absorption-type event
[[D1]] D0 D(t) z2 D1^W junk whose t is not (previous t)-2, i.e. each new transit (round), and the final outcome.
   rounds.py A w T  (or W=...: A=2, w=W-8)"""
import sys
from fw import *
from casc import comp


def rounds(A, w, T, srv, maxsteps=10 ** 10):
    L = [6, 6, 3, 60, T, 0] + [1] * w
    wd, h, q = bword(L, A)
    log = []; prev = None; outc = None
    for x in srv.job(wd, h, q, maxsteps):
        if outc is not None:
            continue
        if x['kind'] == 'HALT':
            it, idx, off = tokpos(x['word'], x['rel'])
            outc = 'HALT(step %d, %d tokens right of head)' % (x['step'], len(it) - idx); continue
        if x['kind'] != 'EV':
            outc = x['kind']; continue
        it, idx, off = tokpos(x['word'], x['rel'])
        r = it[idx + 1:]
        if it[idx] == 1 and off == 1 and len(r) >= 3 and r[0] == 0 and isinstance(r[1], int) and r[2] == 'z2':
            t = r[1]; k = 3; W = 0
            while k < len(r) and r[k] == 1:
                W += 1; k += 1
            if prev is None or t != prev - 2:
                log.append((t, W, comp(r[k:])))
            prev = t
    return log, outc


if __name__ == '__main__':
    srv = Server(M10, 'Bf,E0', 10 ** 9)
    for spec in sys.argv[1:]:
        A, w, T = map(int, spec.split(','))
        log, outc = rounds(A, w, T, srv)
        print('A=%d w=%d T=%d W1=%d:' % (A, w, T, w + 4 + 2 * A), ' | '.join('t=%d W=%d %s' % (t, W, j[:50]) for t, W, j in log), '=>', outc, flush=True)
    srv.close()
