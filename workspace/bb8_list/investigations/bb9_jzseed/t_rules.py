import random, sys
from jzlit import *
random.seed(1)
for name, M in (('CH', CH), ('FW', FW)):
    T = parse(M)
    for rule in ('R1', 'R2', 'R3'):
        used = set(); minrel = 0
        for trial in range(40):
            if rule == 'R1':
                ds = [random.randint(0, 3) for _ in range(random.randint(0, 3))]; a = random.randint(1, 4); b = random.randint(0, 8)
                exp = (tuple(ds), a - 1, b + 3)
            elif rule == 'R2':
                ds = [random.randint(1, 4)] + [random.randint(0, 3) for _ in range(random.randint(0, 3))]; a = 0; b = random.randint(0, 8)
                exp = (tuple([ds[0] - 1] + ds[1:]), b + 2, 1)
            else:
                m = random.randint(0, 3); y = random.randint(0, 3); s = random.randint(0, 6); t = [random.randint(0, 3) for _ in range(random.randint(0, 2))]
                ds = [0] * (m + 1) + [y + 1] + t; a = 0; b = 2 * (m + 1) + s
                exp = (tuple([2] * m + [s + 2, y] + t), 2, 1)
            e = list(exp[0]);
            while e and e[-1] == 0: e.pop()
            exp = (tuple(e), exp[1], exp[2])
            junk = ''
            cells = junk + '0' * 3 + kd_cells(ds, a, b); head = len(junk) + 2
            tp = Tape(cells, head, 3)
            # stop at first return to state D with head at original head cell
            st = run(T, tp, 100000, stop=lambda tp, n: is_kd(tp) is not None, used=used)
            got = is_kd(tp) if st[0] == 'STOP' else None
            minrel = min(minrel, st[2] - head)
            if got != exp: print(name, rule, 'MISMATCH', ds, a, b, exp, got, st)
        print(name, rule, 'used', sorted('%s%d' % (chr(65 + q), c) for q, c in used), 'minrel', minrel)
