"""D2 stage to halt: [P,2,1^k | 1] r j=6 -> family configs and the halt.  python d2halt.py "P" KLIST RLIST [twin]"""
import sys
from tm import *
from tprobe import word, tail
P = [int(x) for x in sys.argv[1].split(',')]
ks = [int(x) for x in sys.argv[2].split(',')]; rs = [int(x) for x in sys.argv[3].split(',')]
M = M12 if len(sys.argv) > 4 else M11
for k in ks:
    for r in rs:
        s = Sim(M, word(P + [2] + [1] * (k + 1), r, 6))
        s.step(); fams = []
        while s.steps < 50_000_000:
            f = at_family_any(s)
            if f:
                ms, rr, jj = f
                fams.append((s.steps, ms if len(ms) < 10 else ms[:6] + ['..%d..' % len(ms)] + ms[-2:], rr, jj))
            if not s.step():
                break
        q = (k - 1) // 5
        pred = P[:-1] + [P[-1] - 2, 2 * r - 2, 3 * q + 5] + [1] * (3 * q - 2) + [0]
        first = fams[0] if fams else None
        ok = bool(fams) and (lambda f0: f0[1] == pred[:len(f0[1])] if len(pred) < 10 else True)(fams[0])
        print('k=%d r=%d: fams %s | %s at %d ones %d' % (k, r, fams, 'HALT' if s.halted else 'RUNNING', s.steps, sum(s.t)), flush=True)
