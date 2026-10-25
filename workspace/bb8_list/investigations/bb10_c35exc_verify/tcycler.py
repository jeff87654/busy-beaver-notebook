"""tcycler.py -- translated-cycler check (right-moving) from a literal configuration, pure Python.
At every new rightmost head position record (state, window of W cells left of the head); a repeat with
the head never going more than W cells left of the earlier record in between proves non-halting."""
from lib import run, word, M10
import sys

def parse(m):
    t = {}
    for si, part in enumerate(m.split('_')):
        for b in (0, 1):
            tr = part[3 * b:3 * b + 3]
            t[(chr(65 + si), b)] = None if tr[0] == '-' else (int(tr[0]), 1 if tr[1] == 'R' else -1, tr[2])
    return t

def check(machine, L, S, R, W=60, maxsteps=3 * 10**6):
    tm = parse(machine)
    tape = {}
    for i, c in enumerate(L): tape[i - len(L)] = int(c)
    for i, c in enumerate(R): tape[i] = int(c)
    pos, st = 0, S
    maxpos = max(tape) if tape else 0
    recs = {}
    minsince = pos
    lastrec = None
    for step in range(maxsteps):
        sym = tape.get(pos, 0)
        tr = tm[(st, sym)]
        if tr is None:
            return 'HALT', step
        w, d, nst = tr
        tape[pos] = w
        pos += d; st = nst
        if pos < minsince: minsince = pos
        if pos > maxpos:
            maxpos = pos
            win = tuple(tape.get(pos - i, 0) for i in range(1, W + 1))
            k = (st, win)
            if k in recs:
                p0, s0, min0 = recs[k]
                # minimum head position since that record (track via list of records)
                mb = min_between(hist, p0)
                mb = min(mb, minsince)
                if mb >= p0 - W:
                    return 'TCYCLER', (s0, step, p0, pos)
            recs[k] = (pos, step, None)
            hist.append((pos, minsince))
            minsince = pos
    return 'UNDECIDED', maxsteps

hist = []
def min_between(h, p0):
    # minimum head position over all intervals after the record at position p0
    m = None
    seen = False
    for (p, mn) in h:
        if seen:
            m = mn if m is None else min(m, mn)
        if p == p0:
            seen = True
    return m if m is not None else p0

if __name__ == '__main__':
    P = [2, 1, 1, 0, 2, 1, 0, 1]
    for body in ([30, 3, 1, 1, 0, 0, 13], [12, 3, 1, 1, 1, 0, 0, 4]):
        toks = P + [40] + body
        snaps, end = run(M10, word(toks), 'G', '0', 10**6)
        hist.clear()
        print(body, check(M10, end[2], end[3], end[4]))
