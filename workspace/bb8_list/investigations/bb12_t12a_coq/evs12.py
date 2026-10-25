"""Event specs (start, target) for T12a: the restart events after n1's round 1, and n1's P1-P4 with a variable far side.
Every spec has the far side as the variable stream l (the part of the far region the event never reads)."""
from shapes import *
from planner8 import V
import evs as N1
FL = [V('l')]
def G(n): return [0] * n
def ones(c): return [x for _ in range(c) for x in tok(1)]
def PP(**v): return [run((1, 0, 1, 1, 0, 1), **v)]            # 1^(2v) in the engine's shape
def JUNK(**v): return [run((0, 0, 0, 0, 0, 1), **v)]          # (100000)^v, i.e. tokens '0 z5' repeated
def WL(*toks): return W(*toks, far=FL)
EV = {}
# round-1 end Bf (FarE k) (1^(w+1) ++ [0]) (f+4): consumes 6 D2s, deposits f, depth + 4
EV['R1END'] = (WL(*[tok(2)] * 6, tok(1), tok(6), G(2), Z(), G(5), tok(1), Z(), Z(), Z(), G(2), Z(), G(2), Z(), G(2), Z(),
                  G(2), Z(), G(2), Z(), ONES(w=1), ones(1), Z(), tok(4, f=1)),
               WL(tok(1), tok(5), G(5), Z(), G(5), Z(), G(5), Z(), G(5), tok(1), Z(), tok(5), ones(3), Z(), tok(3, f=1),
                  ONES(w=1), ones(5), Z(), tok(4)))
EV['E0'] = (WL(G(5), Z(), G(5), Z(), G(5), Z(), G(5), tok(1), Z(), tok(5), ones(3), Z(), Z(), ONES(w=1), ones(1), Z(), tok(0, a=1)),
            WL(G(5), tok(1), Z(), tok(7), G(2), Z(), tok(2), Z(), tok(3), tok(1), Z(), tok(1, a=1), ONES(w=1), ones(1), Z(), tok(4)))
EV['E1'] = (WL(tok(7), G(2), Z(), tok(2), Z(), tok(3), tok(1), Z(), tok(2), ONES(w=1), ones(1), Z(), tok(0, a=1)),
            WL(tok(6), tok(1), tok(2), tok(1), Z(), Z(), Z(), tok(2), Z(), Z(), tok(3, a=1), ONES(w=1), Z(), tok(4)))
EV['E2'] = (WL(tok(6), tok(1), tok(2), tok(1), Z(), Z(), Z(), tok(2), Z(), Z(), ONES(w=1), ones(1), Z(), tok(0, a=1)),
            WL(tok(4), tok(3), Z(), Z(), tok(1), Z(), Z(), Z(), tok(2), Z(), tok(2, a=1), ONES(w=1), Z(), tok(4)))
EV['E3'] = (WL(tok(4), tok(3), Z(), Z(), tok(1), Z(), Z(), Z(), tok(2), Z(), Z(), ONES(w=1), ones(1), Z(), tok(0, a=1)),
            WL(tok(3), Z(), Z(), tok(1), G(2), tok(2), tok(1), Z(), tok(1), tok(1, a=1), ONES(w=1), ones(1), Z(), tok(4)))
EV['E4'] = (WL(tok(2), tok(1), tok(5), G(5), tok(1), Z(), tok(3), Z(), Z(), tok(1), G(2), tok(2), tok(1), Z(), tok(1), tok(2),
               ONES(w=1), ones(1), Z(), tok(0, a=1)),
            WL(tok(1), tok(8), G(2), Z(), G(2), Z(), G(4), Z(), G(3), Z(), Z(), Z(), G(6), tok(3, a=1), ones(2), Z(),
               ONES(w=1), ones(1), Z(), tok(6)))
# the accumulator a = 3x+1 deposited as 3x+4 becomes x junk units (100000)
EV['E5'] = (WL(G(2), Z(), G(2), Z(), G(4), Z(), G(3), Z(), Z(), Z(), G(6), T3(4, x=1), ones(2), Z(), ONES(w=1), ones(3), Z(), tok(6)),
            WL(G(2), tok(5), G(4), JUNK(x=1), tok(3), tok(1), Z(), Z(), Z(), tok(1), Z(), Z(), Z(), tok(9), ONES(w=1), ones(1), Z(), tok(4)))
EV['E6'] = (WL(tok(3), tok(1), Z(), Z(), Z(), tok(1), Z(), Z(), Z(), Z(), ONES(w=1), ones(2), Z(), tok(0, a=1)),
            WL(tok(1), Z(), tok(1), tok(3), Z(), Z(), Z(), tok(3, a=1), ONES(w=1), Z(), tok(4)))
EV['E7'] = (WL(G(5), tok(1), Z(), tok(1), tok(3), Z(), Z(), Z(), ONES(w=1), ones(1), Z(), tok(0, a=1)),
            WL(G(3), tok(1), G(3), tok(2), tok(1, a=1), ONES(w=1), ones(2), Z(), tok(4)))
EV['E8'] = (WL(G(3), tok(2), tok(2), ONES(w=1), ones(1), Z(), tok(0, a=1)),
            WL(G(2), tok(4, a=1), ONES(w=1), ones(1), Z(), tok(6)))
EV['E10'] = (WL(G(3), tok(1), G(2), T3(2, t=1), Z(), ONES(w=1), ones(1), Z(), tok(0, b=1)),
             WL(G(2), tok(3, b=1), PP(t=1), ONES(w=1), ones(2), Z(), tok(4)))
EV['E11'] = (WL(tok(5), G(4), JUNK(M=1), Z(), G(2), ONES(z=1), ones(1), Z(), tok(0, a=1)),
             WL(tok(3), tok(5, a=1), PP(M=1), Z(), ONES(z=1), Z(), tok(6)))
EV['E12'] = (WL(tok(3, p=1), ONES(M=1), ones(5), Z(), ONES(n=1), ones(2), Z(), tok(6)),
             WL(tok(0, p=1), tok(2), tok(5), ONES(M=1), Z(), Z(), Z(), tok(9), ONES(n=1), Z(), tok(4)))
# n1's period events with the far side l (round 2 runs left of the prefix 3 P and the old far region)
def with_far(cfg):
    q, L, R, mode = cfg
    assert L[-1] == BLANK
    return (q, L[:-1] + FL, R, mode)
for k in ('P1', 'P2', 'P3', 'P4'):
    e = N1.EV[k]
    EV['L' + k] = (with_far(e[0]), with_far(e[1])) + tuple(e[2:])
# real accumulators and depths are huge: shift them so that mexp's v = 0 branches stay in the generic regime
def shift(name, **sh):
    S, T = EV[name][:2]
    for v, c in sh.items():
        S = engine.subst(S, v, ((v, 1),), c)
        T = engine.subst(T, v, ((v, 1),), c)
    EV[name] = (S, T) + tuple(EV[name][2:])
for _n in ('E0', 'E1', 'E2', 'E3', 'E6', 'E7', 'E8'):
    shift(_n, a=4, w=2)
shift('E10', b=4, t=2, w=2)
