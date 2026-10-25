import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

import os
os.environ['PATH'] = r'C:\msys64\ucrt64\bin;' + os.environ['PATH']
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect')
from bcfg import BASES, T
import kl
import resid_groupB as rgb

M_tm = '1RB1LA_0RH1RD_1LD1LC_1LE0RF_0LA0LC_---0RG_1RE1RG_0RG1RG'
tt = T('n')

# Test literal small multi-digit configs where all borrows have U >= 14:
for ds, a, b in [
    ([1, 0], 7, 1),
    ([1, 0], 8, 1),
    ([1, 1], 3, 1),
    ([1, 1], 4, 0),
]:
    ev = [x for x in kl.run(M_tm, ds, a, b, 20000000, 0, 5000, T=tt, pall=0) if x[0] in ('K', 'H')]
    # Find the empty-list K-moment K([], a_lit, b_lit)
    empty_ks = [x for x in ev if x[0] == 'K' and x[2] == []]
    Uo, ro = rgb.eval_list(ds, a, b)
    b_pred = 2 if ((Uo + ro) % 2 == 0) else 1
    a_pred = ((Uo + ro - b_pred) // 2) % (rgb.M // 2)
    st_pred = "REBUILD" if (a_pred + b_pred) % 2 == 0 else "HALT"
    print(f"cfg=({ds}, {a}, {b}):")
    print(f"  pred mod {rgb.M//2}: a={a_pred}, b={b_pred} ({st_pred})")
    print(f"  literal empty_ks: {empty_ks}, last={ev[-1]}")
    if empty_ks:
        _, _, _, a_lit, b_lit = empty_ks[0]
        print(f"  literal a mod {rgb.M//2} = {a_lit % (rgb.M//2)}, b = {b_lit}")
