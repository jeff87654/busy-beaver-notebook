# jzlit.py: literal TM helpers for bb9_jzseed (champion labels).  Kd ds a b = 0^inf <D 1^(b+1) 0 1^a (0 1^d)*
import sys
CH = '1RB1RA_0LC0LF_0RD1LC_1RA1RG_1RZ0RA_1LB1LF_1LH1RE_0LI1LH_1LB0LH'
FW = '1RB1RA_0LC0LF_0RD1LC_1RA1RG_1RH0RA_1LB1LF_1RZ1RE_1LI1LI_0RE0LH'
def parse(m):
    T = {}
    for q, part in enumerate(m.split('_')):
        for c in range(2):
            x = part[3*c:3*c+3]
            if x[0] == '-' or x[2] == 'Z' or x[2] == '-' or ord(x[2]) - 65 >= len(m.split('_')): T[(q, c)] = None
            else: T[(q, c)] = (int(x[0]), 1 if x[1] == 'R' else -1, ord(x[2]) - 65)
    return T
def kd_cells(ds, a, b):
    s = '1' * (b + 1) + '0' + '1' * a
    for d in ds: s += '0' + '1' * d
    return s
class Tape:
    def __init__(s, cells='', head=0, q=0):
        s.t = {i: int(c) for i, c in enumerate(cells) if c == '1'}; s.h = head; s.q = q
    def get(s, i): return s.t.get(i, 0)
def is_kd(tp, D=3):
    # state D, head cell 0, all left blank, right finite starting with 1
    if tp.q != D or tp.get(tp.h) != 0: return None
    if any(i < tp.h for i in tp.t): return None
    if tp.get(tp.h + 1) != 1: return None
    mx = max(tp.t); s = ''.join(str(tp.get(i)) for i in range(tp.h + 1, mx + 1))
    i = 0; b = 0
    while i < len(s) and s[i] == '1': b += 1; i += 1
    b -= 1; i += 1; a = 0
    while i < len(s) and s[i] == '1': a += 1; i += 1
    ds = []
    while i < len(s):
        assert s[i] == '0'; i += 1; d = 0
        while i < len(s) and s[i] == '1': d += 1; i += 1
        ds.append(d)
    while ds and ds[-1] == 0: ds.pop()
    return (tuple(ds), a, b)
def run(T, tp, maxsteps, stop=None, used=None):
    """step until halt / maxsteps / stop(tp,steps) true (checked after each step). returns (status, steps, minpos)"""
    n = 0; mn = tp.h
    while n < maxsteps:
        c = tp.get(tp.h); tr = T[(tp.q, c)]
        if used is not None: used.add((tp.q, c))
        if tr is None: return ('HALT', n, mn, (tp.q, c))
        w, d, nq = tr
        if w: tp.t[tp.h] = 1
        else: tp.t.pop(tp.h, None)
        tp.h += d; tp.q = nq; n += 1; mn = min(mn, tp.h)
        if stop and stop(tp, n): return ('STOP', n, mn, None)
    return ('BUDGET', n, mn, None)
