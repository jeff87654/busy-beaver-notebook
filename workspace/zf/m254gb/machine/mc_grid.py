"""Grid / Ev semantics on partitions: for X = ordinal k (k <= 7) evaluate the labelled Grid body
over all pairs (R, C) of set partitions of X (optionally with an empty block), and compare with
|X| = |R|·|C|, |R|,|C| >= 2.  Also Ev's extra conjunct (|R| = 2).   usage: python mc_grid.py [kmax]"""
import sys, json, itertools
from modelcheck import *
import ng_final, ngdsl
f, lab, c = ng_final.chosen()
import importlib
mod = importlib.import_module(c['module']); o = dict(mod.DEFAULT); o.update(c['o'])
grid = ngdsl.ex('R', ngdsl.ex('C', mod.grid(o)))[2][2]       # body with R, C free
evx = mod.ev(o)[2][2]                                           # Grid ∧ ∃F(F=R ∧ Two F)
G = relabel(grid, lab); E = relabel(evx, lab)
def partitions(s):
    s = list(s)
    if not s: yield []; return
    x, rest = s[0], s[1:]
    for p in partitions(rest):
        for i in range(len(p)):
            yield p[:i] + [p[i] | {x}] + p[i+1:]
        yield p + [frozenset([x])]
kmax = int(sys.argv[1]) if len(sys.argv) > 1 else 6
for k in range(kmax + 1):
    X = ordinal(k); U = powerset(X)
    parts = [frozenset(p) for p in partitions(X)]
    parts += [p | {frozenset()} for p in parts]
    bad = 0; sizes = set(); evs = set()
    for R in parts:
        for C in parts:
            env = {lab['n']: X, lab['R']: R, lab['C']: C}
            g = ev(G, env, U)
            want = (all(len(r) > 0 for r in R) and all(len(cc) > 0 for cc in C) and
                    all(len(r & cc) == 1 for r in R for cc in C) and len(R) >= 2 and len(C) >= 2) or (k == 0 and not R and not C)
            if g != want: bad += 1
            if g: sizes.add((len(R), len(C)))
            if g and ev(E, env, U): evs.add((len(R), len(C)))
    print(f'k={k}: partitions {len(parts)}, grid mismatches {bad}, grid shapes {sorted(sizes)}, Ev shapes {sorted(evs)}', flush=True)
