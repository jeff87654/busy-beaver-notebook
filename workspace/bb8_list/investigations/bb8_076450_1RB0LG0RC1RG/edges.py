"""Literal run from a start word; print tape (8-blocks aligned to the right end of the word) at every
visit of the head to the leftmost nonblank-or-new position (any state)."""
import sys
from tmlib import *
tm = {'main': MAIN, 'v1': VAR1, 'v2': VAR2}[sys.argv[1]]
w = expand(sys.argv[2]); maxsteps = int(sys.argv[3]); stopword = sys.argv[4] if len(sys.argv) > 4 else None
sim = Sim(tm, w, pad=4000)
right_end = sim.pos + len(w)   # index of last cell of word
def blocks():
    t = sim.tape
    lo = sim.lo
    while lo < sim.pos and t[lo] == 0: lo += 1
    lo = min(lo, sim.pos)
    # align so that blocks end at right_end
    start = right_end - ((right_end - lo) // 8 + 1) * 8 + 1
    out = []
    i = start
    while i <= right_end:
        blk = ''.join(str(c) for c in t[i:i+8])
        if i <= sim.pos < i + 8:
            k = sim.pos - i
            blk = blk[:k] + '[' + ST[sim.state] + ']' + blk[k:]
        out.append(blk)
        i += 8
    # run-length compress identical blocks
    res = []; j = 0
    while j < len(out):
        k = j
        while k + 1 < len(out) and out[k+1] == out[j]: k += 1
        res.append(out[j] + ('^%d' % (k - j + 1) if k > j else ''))
        j = k + 1
    return ' '.join(res)
last = None
while sim.steps < maxsteps:
    if not sim.step(): print('HALT', sim.steps); break
    t = sim.tape
    if not any(t[sim.lo:sim.pos]) and t[sim.pos] == 0:
        if last != sim.steps - 1:
            print('%7d %s' % (sim.steps, blocks()))
        last = sim.steps
    if stopword is not None and sim.state == 0 and sim.at_left_A0() and sim.word() == expand(stopword):
        print('reached stopword at', sim.steps); break
