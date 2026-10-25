"""print the tape (compact) each time the head turns from moving left to moving right at a position left of all previous lows... or every turn with full tape"""
import sys
from bsim import *
def cfg_str(t, h, q, lo, hi):
    s = ''.join(map(str, t[lo:h])) + '[' + q + ']' + ''.join(map(str, t[h:hi]))
    return s
def run_turns(word, head, q, maxsteps, mode='minturn', T=TT, show=None):
    PAD = 1 << 14
    t = bytearray(PAD) + bytearray(int(c) for c in word) + bytearray(PAD)
    h = head + PAD; steps = 0; dprev = 0
    lo0 = PAD
    out = []
    while steps < maxsteps:
        s = t[h]; tr = T[(q, s)]
        if tr is None:
            out.append((steps, 'HALT', q)); break
        w, d, q2 = tr
        if dprev == -1 and d == 1:
            out.append((steps, h - PAD, q, s, bytes(t)))
        dprev = d
        t[h] = w; h += d; q = q2; steps += 1
    return out, PAD
