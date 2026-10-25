import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from segs import *
from validate import concretize
from tr2 import rle
def run_turns(s, t, vals, maxsteps=20000):
    q, l, h, r = concretize(s, vals)
    goal = concretize(t, vals)
    # tape as list with head index
    tape = list(reversed(l)) + [h] + r
    pos = len(l)
    prevd = 0; n = 0
    def show(tag=''):
        w = ''.join(map(str, tape)); 
        print(n, q, tag, rle(w[:pos]) + ' [' + w[pos] + '] ' + rle(w[pos+1:]))
    show('start')
    while n < maxsteps:
        c = tape[pos]
        tr = pl.T.get((q, c))
        if tr is None: print('HALT'); return
        w, d, q2 = tr
        tape[pos] = w
        pos += d
        if pos < 0: tape.insert(0, 0); pos = 0
        if pos >= len(tape): tape.append(0)
        q = q2; n += 1
        if prevd and d != prevd: show('<' if d < 0 else '>')
        prevd = d
        # goal check
        g = concretize(t, vals)
        # compare
        ll = tape[:pos][::-1]; rr = tape[pos+1:]
        from validate import same
        if same((q, ll, tape[pos], rr), g):
            show('GOAL'); return
if __name__ == '__main__':
    nm = sys.argv[1]
    vals = eval(sys.argv[2])
    S = segs()
    s, t, _ = S[nm]
    run_turns(s, t, vals)
