"""Craft / recognize the outer (Ce) configurations of the M13 core-label machine.

Ce(p,a,c,d,e):
  left  : (10)^p 1^(a+2) 0^inf
  head  : state A on the first cell of the right side
  right : (10)^c 0 1^d [0 1^e] 0^inf
For c=0 the head cell is the separator 0 (right = 0 1^d [0 1^e] ...).
"""
from tm import parse

A = 'A'
CORE = '1RI0LL_1RA1RC_0LD1LG_0RE1LD_1RZ1RF_1LI0RM_1RM0LH_1LG1LH_0LK1RJ_1RE0LA_1RA0RF_1LH1LA_1RB1RM'


def craft(p, a, c, d, e=None, base=20):
    tape = {}
    pos = base
    for _ in range(p):
        tape[pos] = 1; tape[pos + 1] = 0; pos += 2
    for _ in range(a + 2):
        tape[pos] = 1; pos += 1
    head = pos
    if c > 0:
        for _ in range(c):
            tape[pos] = 1; tape[pos + 1] = 0; pos += 2
        tape[pos] = 0; pos += 1
    else:
        tape[pos] = 0; pos += 1
    for _ in range(d):
        tape[pos] = 1; pos += 1
    if e is not None:
        tape[pos] = 0; pos += 1
        for _ in range(e):
            tape[pos] = 1; pos += 1
    return tape, head


def read_cfg(tape, pos, q, with_e=False):
    """If the head is on the first 1 of a (10)^c block (c>=1) with a clean
    Ce-shaped tape around it, return dict(p,a,c,d,e).  Else None."""
    if q != A or tape.get(pos, 0) != 1 or tape.get(pos + 1, 0) != 0:
        return None
    i = pos - 1
    ones_a = 0
    while i >= 0 and tape.get(i, 0) == 1:
        ones_a += 1; i -= 1
    if ones_a < 2 or ones_a % 2:
        return None
    p = 0
    while i >= 1 and tape.get(i, 0) == 0 and tape.get(i - 1, 0) == 1:
        p += 1; i -= 2
    if i < 1:
        return None
    for k in range(0, i + 1):
        if tape.get(k, 0) != 0:
            return None
    # right: (10)^c 0 1^d [0 1^e]
    j = pos; c = 0
    while tape.get(j, 0) == 1 and tape.get(j + 1, 0) == 0:
        c += 1; j += 2
    if c < 1:
        return None
    if tape.get(j, 0) != 0:
        return None
    j += 1
    d = 0
    while tape.get(j, 0) == 1:
        d += 1; j += 1
    e = None
    if with_e:
        if tape.get(j, 0) != 0:
            return None
        j += 1
        e = 0
        while tape.get(j, 0) == 1:
            e += 1; j += 1
    # tail must be all zero
    keys = [k for k in tape if tape[k]]
    if keys and max(keys) > j:
        return None
    return dict(p=p, a=ones_a - 2, c=c, d=d, e=e)


def run_cfg(m, tape, head, steps, with_e=False, q0='A'):
    T = parse(m)
    q, pos = q0, head
    for s in range(1, steps + 1):
        sym = tape.get(pos, 0)
        t = T[ord(q) - 65][sym]
        if t is None:
            return ('HALT', s, None)
        w, mv, nq = t
        tape[pos] = w; pos += mv
        if nq == 'Z':
            return ('HALT', s, None)
        q = nq
        cfg = read_cfg(tape, pos, q, with_e)
        if cfg is not None:
            return ('RET', s, cfg)
    return ('TIME', steps, None)
