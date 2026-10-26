"""Probe the M13 core with a third counter e in several tape layouts.

Ce3(p,a,c,d,e) right side, layout variants:
  L1: (10)^c 0 1^d 0 1^e 0^inf
  L2: (10)^c 0 1^d 0 0 1^e 0^inf
Head starts in state A on the first 1 of (10)^c (c>=1) or on the separator 0 (c=0).
We only report the first return to the same shape, plus halts.
"""
from tm import parse

CORE = ('1RI0LL_1RA1RC_0LD1LG_0RE1LD_1RZ1RF_1LI0RM_1RM0LH_1LG1LH_0LK1RJ_'
        '1RE0LA_1RA0RF_1LH1LA_1RB1RM')


def craft3(p, a, c, d, e, gap=1, base=20):
    """gap = number of zeros between the d block and the e block (1 or 2)."""
    tape, pos = {}, base
    for _ in range(p):
        tape[pos] = 1; tape[pos + 1] = 0; pos += 2
    for _ in range(a + 2):
        tape[pos] = 1; pos += 1
    head = pos
    for _ in range(c):
        tape[pos] = 1; tape[pos + 1] = 0; pos += 2
    tape[pos] = 0; pos += 1          # separator after c
    for _ in range(d):
        tape[pos] = 1; pos += 1
    tape[pos] = 0; pos += 1          # separator after d
    for _ in range(gap - 1):
        tape[pos] = 0; pos += 1
    for _ in range(e):
        tape[pos] = 1; pos += 1
    return tape, head


def read3(tape, pos, q, gap=1):
    if q != 'A' or tape.get(pos, 0) != 1 or tape.get(pos + 1, 0) != 0:
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
    if i < 1 or any(tape.get(k, 0) for k in range(i + 1)):
        return None
    j = pos; c = 0
    while tape.get(j, 0) == 1 and tape.get(j + 1, 0) == 0:
        c += 1; j += 2
    if c < 1 or tape.get(j, 0) != 0:
        return None
    j += 1
    d = 0
    while tape.get(j, 0) == 1:
        d += 1; j += 1
    if tape.get(j, 0) != 0:
        return None
    j += 1
    for _ in range(gap - 1):
        if tape.get(j, 0) != 0:
            return None
        j += 1
    e = 0
    while tape.get(j, 0) == 1:
        e += 1; j += 1
    if any(v for k, v in tape.items() if k > j):
        return None
    return dict(p=p, a=ones_a - 2, c=c, d=d, e=e)


def run3(m, tape, head, steps, gap=1):
    T = parse(m); q, pos = 'A', head
    for s in range(1, steps + 1):
        sym = tape.get(pos, 0)
        t = T[ord(q) - 65][sym]
        if t is None or t[2] == 'Z':
            return ('HALT', s, None)
        w, mv, nq = t
        tape[pos] = w; pos += mv; q = nq
        cfg = read3(tape, pos, q, gap)
        if cfg is not None:
            return ('RET', s, cfg)
    return ('TIME', steps, None)


if __name__ == '__main__':
    cases = [
        (4, 8, 0, 2, 2), (4, 8, 0, 3, 2), (4, 8, 0, 2, 3),
        (4, 8, 0, 0, 2), (4, 8, 0, 0, 3), (4, 8, 0, 0, 0),
        (4, 8, 0, 0, 1), (4, 8, 0, 1, 2),
        (2, 8, 0, 0, 2), (2, 8, 0, 0, 0),
    ]
    for gap in (1, 2):
        print(f'==== layout gap={gap} ====')
        for (p, a, c, d, e) in cases:
            t, h = craft3(p, a, c, d, e, gap=gap)
            print((p, a, c, d, e), run3(CORE, t, h, 4000, gap=gap))
