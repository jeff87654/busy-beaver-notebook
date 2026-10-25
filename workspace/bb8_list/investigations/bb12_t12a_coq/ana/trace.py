"""trace.py: literal run from a word, print turning points / checkpoints."""
import sys, pickle
from bsim import *
def tape_str(t, a, b, h):
    s = ''.join(map(str, t[a:b]))
    return s
def run_trace(word, head, q, maxsteps, every=None, tp=True, lo_win=60, T=TT):
    PAD = 1 << 14
    t = bytearray(PAD) + bytearray(int(c) for c in word) + bytearray(PAD)
    h = head + PAD; steps = 0; d_prev = 0
    base = PAD
    while steps < maxsteps:
        s = t[h]; tr = T[(q, s)]
        if tr is None:
            print('HALT', q, s, steps); return
        w, d, q2 = tr
        if tp and d != d_prev and d_prev != 0:
            a = t.find(1); b = t.rfind(1)
            print('%7d turn %s pos %d  [%s] %s' % (steps, q, h - base, ''.join(map(str, t[max(a, h - lo_win):h])) + '|' + ''.join(map(str, t[h:min(b + 1, h + lo_win)])), ''))
        d_prev = d
        t[h] = w; h += d; q = q2; steps += 1
