"""small2e.py TAG MACHINE [STEPS]: from E-configs K(;A;B0), A=1..10, trace real E-moments (empty list, b=B0) and halts:
shows the sequence of exhaustion accumulators (small worlds; consecutive E's) -> is the 2nd-E parity structural?"""
import idle, sys
from bcfg import *
tag, M = sys.argv[1], sys.argv[2]; steps = int(sys.argv[3]) if len(sys.argv) > 3 else 5 * 10**7
B0 = BASES[tag][2]; t = T(tag)
for A in range(1, 11):
    ev = kl.run(M, [], A, B0, steps, 0, 400, T=t, pall=0)
    seq = []; lastlen = None
    for e in ev[1:]:
        if e[0] == 'K' and e[4] == B0:
            if not e[2]: seq.append(f"E{e[3]}")
            elif lastlen is None or (seq and seq[-1].startswith('E')): seq.append(f"L{len(e[2])}")
            lastlen = len(e[2])
        elif e[0] == 'H': seq.append(f"HALT@{e[1]}")
    print(A, ' '.join(seq[:14]))
