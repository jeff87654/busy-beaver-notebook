"""accelerated abstract run: macro = full countdown of d_1 then borrow. Reports borrow events with position, N, b, margin."""
import sys
from eng import borrow, to_runs
from drv import show
def run(ds, a, b, maxbits=4000, maxev=10**6, verbose=False):
    ev = 0; minm = None; r4 = 0
    while ev < maxev:
        x = b + 2 * a
        v = ds[-1][0]
        if v > 0:
            if v > maxbits: return ('BIG', ev, r4, minm, len(ds))
            x = (x + 2) * (1 << v) - 2
            ds = ds[:-1] + [(0, ds[-1][1])]
        if x.bit_length() > maxbits: return ('BIG', ev, r4, minm, len(ds))
        j = max([i for i, (vv, m) in enumerate(ds) if vv > 0], default=-1)
        kz = len(ds) - 1 - j
        m = x - kz - 1; minm = m if minm is None else min(minm, m)
        if j < 0:
            r4 += 1
            if verbose: print('R4 #%d N=%d b=%d' % (r4, len(ds), x) if x < 10**12 else 'R4 #%d N=%d b~2^%d' % (r4, len(ds), x.bit_length()))
        r = borrow(ds, x)
        if r is None: return ('INVALID', ev, r4, minm, len(ds), show(to_runs(ds, 0, 0))[:100], x)
        ds, a, b = r; ev += 1
    return ('MAXEV', ev, r4, minm, len(ds))
if __name__ == '__main__':
    from drv import parse_ds
    ds = [(x // 2, x % 2) for x in parse_ds(sys.argv[1])]
    print(run(ds, int(sys.argv[2]), int(sys.argv[3]), maxbits=int(sys.argv[4]), verbose=True))
