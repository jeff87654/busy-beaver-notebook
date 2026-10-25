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
B0 = BASES[tag][2]
for A in (1, 3):
    ev = kl.run(M, [], A, B0, 500000, 0, 400, T=T(tag), pall=1)
    print(f"=== E({A}) total events: {len(ev)} ===")
    for e in ev[-15:]:
        print(" ", e)

ev_b = kl.blank(M, 500000, 400, T=T(tag))
print(f"=== BLANK total events: {len(ev_b)} ===")
for e in ev_b[:30]:
    print(" ", e)
