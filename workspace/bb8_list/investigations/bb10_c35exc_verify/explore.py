"""explore.py PATTERN... : literal first-event results for token patterns (space separated, 'y' = accumulator values 4..6)"""
import sys
from lib import bforms, ctok, diff, M10
P = [2, 1, 1, 0, 2, 1, 0, 1]
def first(toks, N=2 * 10**6):
    bf, end = bforms(M10, toks, N, maxsnap=2)
    return (bf[1][1], bf[1][0]) if len(bf) > 1 else (None, end)
for pat in sys.argv[1:]:
    for y in (4, 5, 6, 7):
        body = [int(v) for v in pat.split(',')]
        toks = P + [20] + body + [0, y]
        t, info = first(toks)
        if t is None:
            print(pat, 'y=%d' % y, '-> NONE', info[0], info[1])
        else:
            k, a1, a2 = diff(toks, t)
            print(pat, 'y=%d' % y, ' ', ctok(a1), '->', ctok(a2), ' [%d]' % info)
