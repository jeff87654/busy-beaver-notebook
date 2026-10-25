"""D0-family shapes for mexp (left streams nearest-first; head in B on the blank right).
D0(l,s,y,P,L,t) = l 1 (10)^(s+1) 1 (10)^y 011 (100)^P 1^L 11 (11111100)^t 1001 B>"""
from common import *
TB = (0, 0, 1, 1, 1, 1, 1, 1)
def lin_run(blk, const, **var):
    out = list(blk) * const
    if var: out.append(run(blk, **var))
    return out
PB = 1
KL = 0
def D0(scon, svar, ycon, yvar, Pcon, Pvar, Lcells, tcon=0, mid=None, far=None):
    """scon/svar: s+1 = scon + svar-run; ycon/yvar similarly for y; Lcells: list of left-stream items for 1^L;
    mid: extra frozen cells (nearest-first) between the D0 part and l."""
    left = [1, 0, 0, 1] + list(TB) * tcon + [run(TB, t=1), 1, 1] + Lcells + [0, 0, 1] * (Pcon - (KL if Pvar else 0)) + ([run((0, 0, 1) * PB, **{Pvar: 1})] + [0, 0, 1] * KL if Pvar else [])
    left += [1, 1, 0] + lin_run((0, 1), ycon, **({yvar: 1} if yvar else {})) + [1] + lin_run((0, 1), scon, **({svar: 1} if svar else {}))
    left += (mid or []) + [1] + (far if far is not None else [V('l')])
    return ('B', left, [BLANK], '>')
