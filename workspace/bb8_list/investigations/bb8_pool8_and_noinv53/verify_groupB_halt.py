import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

import os
os.environ['PATH'] = r'C:\msys64\ucrt64\bin;' + os.environ['PATH']
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect')
from bcfg import BASES, T
import kl

M = '1RB1LA_0RH1RD_1LD1LC_1LE0RF_0LA0LC_---0RG_1RE1RG_0RG1RG'
tt = T('n')
for (aa, bb) in [(4, 0), (4, 1)]:
    for d in range(1, 7):
        ev = [x for x in kl.run(M, [d], aa, bb, 500000, 0, 500, T=tt, pall=0) if x[0] in ('K', 'H')]
        print(f"K([{d}], {aa}, {bb}) -> {ev[:6]}")
