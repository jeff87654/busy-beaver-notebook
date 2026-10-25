"""instantiate a symbolic config with concrete values -> literal word view / simulator"""
from common import *
from planner8 import is_run
from tm_old import rle, Sim
LPAD = [1, 0] * 9 + [1]   # VAR l is shown as a D9 token
def side_bits(side, vals):
    out = []
    for t in side:
        if isinstance(t, int): out.append(t)
        elif is_run(t):
            c = sum(k * vals[v] for v, k in t[2]); out.extend(list(t[1]) * c)
        elif t == BLANK: break
        else: out.extend(LPAD); break
    return out
def word(cfg, vals):
    q, L, R, mode = cfg
    l = side_bits(L, vals)[::-1]; r = side_bits(R, vals)
    w = ''.join(map(str, l + r)); hp = len(l) - (1 if mode == '<' else 0)
    return w, hp, q
def view(cfg, vals):
    w, hp, q = word(cfg, vals)
    return rle(w, hp, q)
def sim(cfg, vals):
    w, hp, q = word(cfg, vals)
    s = Sim(TM, '0' * 50 + w + '0' * 50, 50 + hp, q)
    return s
