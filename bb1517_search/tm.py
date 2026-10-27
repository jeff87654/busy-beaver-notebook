"""Minimal 2-symbol Turing machine simulator, bbchallenge notation.

A machine string is N segments separated by '_', e.g. 1RI0LL_1RA1RC_...
segment i gives (write, move, next) for state i on symbol 0 and symbol 1.
'---' = undefined => halting transition.
"""
import sys


def parse(m):
    segs = m.split('_')
    tab = []
    for seg in segs:
        tab.append([seg[:3], seg[3:]])

    def dec(t):
        if t == '---':
            return None
        return (int(t[0]), 1 if t[1] == 'R' else -1, t[2])

    return [[dec(tab[i][0]), dec(tab[i][1])] for i in range(len(tab))]


def run(m, steps, start='A', tape=None, pos=0, trace_every=0, stop_cond=None):
    T = parse(m)
    if tape is None:
        tape = {}
    q = start
    for s in range(1, steps + 1):
        sym = tape.get(pos, 0)
        t = T[ord(q) - 65][sym]
        if t is None:
            return ('HALT', s - 1, tape, pos, q)
        w, mv, nq = t
        tape[pos] = w
        pos += mv
        if nq == 'Z':
            return ('HALT', s, tape, pos, 'Z')
        q = nq
        if trace_every and s % trace_every == 0:
            print(s, q, pos, tape_sig(tape, pos))
        if stop_cond is not None and stop_cond(s, q, tape, pos):
            return ('STOP', s, tape, pos, q)
    return ('TIME', steps, tape, pos, q)


def tape_sig(tape, pos, lo=None, hi=None):
    if not tape:
        return '0^@%d' % pos
    lo = min(tape) if lo is None else lo
    hi = max(tape) if hi is None else hi
    return '%s @%d [%d..%d]' % (''.join(str(tape.get(i, 0)) for i in range(lo, hi + 1)), pos, lo, hi)


def ones(tape):
    return sum(1 for v in tape.values() if v == 1)


def show_run(m, steps, **kw):
    st, s, tape, pos, q = run(m, steps, **kw)
    print('status=%s steps=%d ones=%d state=%s' % (st, s, ones(tape), q))
    print(tape_sig(tape, pos))
    return st, s, tape, pos, q


if __name__ == '__main__':
    show_run(sys.argv[1], int(sys.argv[2]))
