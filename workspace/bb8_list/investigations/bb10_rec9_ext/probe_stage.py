"""Literal outcomes of a cached machine's stage-N input over a range of one parameter (others fixed).
Usage: python probe_stage.py MACHINE N PARAM start step count [P=v ...] [--canon Q] [--budget B]"""
import sys, subprocess, os
from pathlib import Path
import follow3 as F
from stage_input import replay
args = sys.argv[1:]
canon, budget = None, 1000000000
if '--canon' in args:
    i = args.index('--canon'); canon = args[i + 1]; del args[i:i + 2]
if '--budget' in args:
    i = args.index('--budget'); budget = int(args[i + 1]); del args[i:i + 2]
machine, n, par, start, step, count = args[0], int(args[1]), args[2], int(args[3]), int(args[4]), int(args[5])
fixed = dict(kv.split('=') for kv in args[6:])
sym, params, st = replay(machine, n)
print('stage input:', F.fmt_sym(sym), 'state', st)
for j in range(count):
    vals = {}
    for p in F.params_in(sym):
        if p == par:
            vals[p] = start + j * step
        elif p in fixed:
            vals[p] = int(fixed[p])
        elif params[p].exact and params[p].x <= 20000:
            vals[p] = params[p].x
        else:
            vals[p] = 200 + (params[p].m(3) - 200) % 3
    try:
        w = F.word_of(F.inst(sym, vals))
    except F.Fail as ex:
        print(vals, 'FAIL', ex); continue
    o = F.run_hyb(machine, w, budget, start=st, canon=canon or st)
    print(vals[par], o['raw'][:230], flush=True)
