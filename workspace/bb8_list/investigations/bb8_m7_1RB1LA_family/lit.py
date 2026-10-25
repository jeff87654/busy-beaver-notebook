import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from w_fam import *
from validate import concretize, strip
def run_show(s, vals, states='C', nmax=6, maxsteps=3000, mode_filter=None):
    q, l, h, r = concretize(s, vals)
    l, r = list(l), list(r)
    cnt = 0
    for n in range(maxsteps):
        if q in states:
            L = ''.join(map(str, [h] + l))
            Rr = ''.join(map(str, r))
            print(n, q, 'L(head first)=', L[:60], '| R=', Rr[:40])
            cnt += 1
            if cnt >= nmax: return
        tr = pl.T.get((q, h))
        if tr is None: print('HALT'); return
        w, d, q = tr
        if d == 1:
            l.insert(0, w); h = r.pop(0) if r else 0
        else:
            r.insert(0, w); h = l.pop(0) if l else 0
if __name__ == '__main__':
    R = rules2()
    s, t = R['R3Am']
    run_show(s, {'k': 0, 'r': 0, 'y': 0}, states='C', nmax=5)
