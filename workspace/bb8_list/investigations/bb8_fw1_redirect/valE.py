import idle, sys
from bcfg import *
for tag in BASES:
    M, tt, B0, fam = BASES[tag]; out = []
    for A in range(1, 9):
        ev = kl.run(M, [], A, B0, 10**6, 0, 400, T=T(tag), pall=1)
        e = [x for x in ev[1:] if x[0] == 'H' or (x[0] == 'K' and x[4] == B0)]
        out.append(f"{A}:" + ('H' if e and e[0][0] == 'H' else (f"[{','.join(map(str,e[0][2][:3]))}..({len(e[0][2])})]{e[0][3]}" if e else '?')))
    print(tag, fam, ' '.join(out), flush=True)
