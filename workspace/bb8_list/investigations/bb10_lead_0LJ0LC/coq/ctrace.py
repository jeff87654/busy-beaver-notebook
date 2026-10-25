"""Concrete trace with compressed tape at direction changes / given states (for designing waypoints)."""
import sys, re
from common import *
def rle(cells):
    s = ''.join(map(str, cells))
    out = []; i = 0
    while i < len(s):
        best = None
        for L in (2, 3, 4, 5, 6):
            blk = s[i:i+L]
            if len(blk) < L: break
            r = 1
            while s[i+r*L:i+(r+1)*L] == blk: r += 1
            if r >= 3 and (best is None or r*L > best[0]*best[1]): best = (r, L, blk)
        if best:
            out.append('(%s)^%d' % (best[2], best[0])); i += best[0]*best[1]
        else:
            out.append(s[i]); i += 1
    return ' '.join(out)
def run(ns, maxs=100000, every=None, states=None):
    w = '1' + ''.join('10'*n + '1' for n in ns)
    PAD = 3000
    tape = [0]*PAD + [int(c) for c in w] + [0]*PAD
    pos = PAD + len(w); q = "G"; prevd = None
    for st in range(1, maxs+1):
        s = tape[pos]; tr = pl.T[(q, s)]
        if tr is None: print('HALT', st); return
        tape[pos] = tr[0]; pos += tr[1]; q = tr[2]
        hi = max(i for i, c in enumerate(tape) if c) if any(tape) else pos
        lo = min(i for i, c in enumerate(tape) if c)
        show = (prevd is not None and tr[1] != prevd) if states is None else (q in states)
        prevd = tr[1]
        if show:
            L = rle(tape[lo:pos]); R = rle(tape[pos:hi+1])
            print('%5d %s %s | %s' % (st, q, L, R))
        if q == 'G' and tape[pos] == 0 and pos > hi:
            w = ''.join(map(str, tape[lo:pos]))
            import re as _re
            if _re.fullmatch(r'1((10)*1)*', w): print('END', st, 'parsed'); return
            print('G-EVENT (no parse)', st)
run(eval(sys.argv[1]), states=sys.argv[2] if len(sys.argv) > 2 else None)
