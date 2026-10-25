import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

import os
os.environ['PATH'] = r'C:\msys64\ucrt64\bin;' + os.environ['PATH']
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect')
from bcfg import BASES, T
import kl

M = '1RB1LA_0RH1RD_1LD1LC_1LE0RF_0LA0LC_---0RG_1RE1RG_0RG1RG'
tag = 'n'
tt = T(tag)

print("=== R2 on K([2, 3], a, b) for b in (0, 1, 2), a in 1..6 ===")
for b in (0, 1, 2):
    outs = []
    for a in range(1, 7):
        ev = [x for x in kl.run(M, [2, 3], a, b, 100000, 2, 200, T=tt, pall=0) if x[0] in ('K', 'H')]
        e = ev[-1]
        outs.append(f"a={a}->{e[2]}:{e[3]},{e[4]}" if e[0] == 'K' else f"a={a}->H:{e[1]}")
    print(f"  b={b}: " + "  ".join(outs))

print("\n=== Bk on K([2, 2] + [0]*k, a, b) for k=1..6, b in (0, 1, 2) ===")
for k in range(1, 7):
    for b in (0, 1, 2):
        outs = []
        for a in range(2*k + 3, 2*k + 7):
            ev = [x for x in kl.run(M, [2, 2] + [0]*k, a, b, 100000, 2, 200, T=tt, pall=0) if x[0] in ('K', 'H')]
            e = ev[-1]
            outs.append(f"a={a}->{e[2]}:{e[3]},{e[4]}" if e[0] == 'K' else f"a={a}->H:{e[1]}")
        print(f"  k={k} b={b}: " + "  ".join(outs))
