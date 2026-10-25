from lib import *
import sys
def show(toks, N=10**6, nb=4):
    bf, end = bforms(M10, toks, N, maxsnap=nb + 1)
    out = [ctok(toks)]
    prev = toks
    for s, t in bf[1:]:
        k, a1, a2 = diff(prev, t)
        out.append('[%d] %s -> %s' % (s, ctok(a1), ctok(a2)))
        prev = t
    if len(bf) <= nb:
        out.append('END %s %d %s|%s|%s' % (end[0], end[1], rle(end[2])[-80:], end[3], end[4][:40]))
    print(' ;; '.join(out))
for x in (0, 2, 3):
    for left in ([], [4], [7], [5], [6], [3], [2], [0]):
        for k in (0, 1, 2):
            for y in (4, 16):
                show([2, 1, 1, 0, 2, 1, 0, 1, 9] + left + [x] + [1] * k + [0, y])
