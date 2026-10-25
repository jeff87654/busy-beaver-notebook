"""n1 endgame: (1) P2 with m = 1: [2^k,5,1,0^3,1,P,0,1^w | R] (literal); (2) after CLR(R+2 -> D0):
far'' + [0, 1^w'' | F] (literal) -> HALT?   endg.py KLIST WLIST [F]"""
import sys
from fw import *
from n1sim import literal, flab
ks = eval(sys.argv[1]); ws = eval(sys.argv[2]); Fs = eval(sys.argv[3]) if len(sys.argv) > 3 else [520]
P, R = 1480, 640
for k in ks:
    for w in ws:
        kind, res, st, evs = literal('', [2] * k + [5, 1, 0, 0, 0, 1, P, 0] + [1] * w, R, 10 ** 11)
        if kind != 'B':
            print('k=%d w=%d: P2(m=1) ->' % (k, w), kind, show(res)[:200]); continue
        far2, L2, A2 = res
        out = []
        for F in Fs:
            L3 = [0] + L2[1:]
            k3, r3, st3, ev3 = literal(far2, L3, F, 10 ** 11)
            if k3 == 'B':
                out.append('F=%d:B %s' % (F, flab(*r3)[:80]))
            else:
                out.append('F=%d:%s%s%d ones=%s' % (F, k3, r3.get('q', ''), r3.get('c', -1), r3.get('ones')))
        print('k=%d w=%d: P2(m=1) -> %s ; then %s' % (k, w, flab(far2, L2, A2)[:100], ' | '.join(out)), flush=True)
