"""Crafted-configuration runner. Config string: cells as chars, head marked by 'X>' (reads next cell) or '<X' (reads previous cell)."""
import re
from rsim import Sim
def build(m, left, st, right, face='R'):
    s = Sim(m)
    for ch in left: Sim.push(s.L, int(ch), 1)
    for ch in reversed(right): Sim.push(s.R, int(ch), 1)
    s.st = st; s.face = face
    return s
def cells(s):
    l = ''.join(str(a)*n for a,n in s.L); r = ''.join(str(a)*n for a,n in reversed(s.R))
    return l, r
def run_until(s, pred, maxmacro=10**7):
    for _ in range(maxmacro):
        if s.halted: return 'HALT'
        if pred(s): return 'OK'
        s.step()
    return 'TIMEOUT'
def norm(l, r):
    return l.lstrip('0'), r.rstrip('0')
