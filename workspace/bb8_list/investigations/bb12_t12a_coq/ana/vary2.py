import sys, json
from macro2 import *
def toks(wd):
    t = parse_tail(wd); st = t[-1][0]
    return wd[:st], [m for _, m in t][::-1]
def runv(k, w, f, reps, n=22):
    R = Run(reps, verbose=False)
    wd = r1end(k, w, f)
    R.go(wd, len(wd), 'H', nmax=n)
    return R.events
if __name__ != "__main__": raise SystemExit
k, w = 17, 36
base = runv(k, w, 40, {})
def diff(ev, label):
    for i, (a, b) in enumerate(zip(base, ev)):
        for key in ('inp', 'out'):
            fa, ta = toks(a[key]); fb, tb = toks(b[key])
            if fa != fb or ta != tb:
                d = []
                if len(ta) == len(tb):
                    d = [(j, x, y) for j, (x, y) in enumerate(zip(ta, tb)) if x != y]
                print('  %s E%02d %s: far %d->%d %s toks %s' % (label, i, key, len(fa), len(fb), 'same' if fa == fb else 'DIFF', d if d else ('len %d->%d' % (len(ta), len(tb)))))
for i in range(16):
    for v in (82, 124):
        print('rep#%d = %d' % (i, v))
        diff(runv(k, w, 40, {i: v}), 'r%d=%d' % (i, v))
for v in (82, 124):
    print('f = %d' % v); diff(runv(k, w, v, {}), 'f=%d' % v)
