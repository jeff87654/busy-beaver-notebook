import sys, json
from macro2 import *
def show(wd):
    far, tk = fmt_word(wd)
    return '(%d) %s | %s' % (len(far), far[-24:], comp(tk))
def runv(k, w, f, reps, n=22):
    R = Run(reps, verbose=False)
    wd = r1end(k, w, f)
    R.go(wd, len(wd), 'H', nmax=n)
    return R.events
base = runv(17, 330, 40, {})
for i, e in enumerate(base):
    print('E%02d IN  %s' % (i, show(e['inp']))[:260])
    print('    OUT %s   [%s steps, %s]' % (show(e['out'])[:220], e.get('steps'), e.get('reads')))
