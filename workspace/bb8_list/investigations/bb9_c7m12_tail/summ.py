"""Summarise fol9b logs: python summ.py fol/b_*.log"""
import re, sys
for f in sys.argv[1:]:
    L = open(f).read().splitlines()
    evs = [l for l in L if re.match(r'EV\d+ @', l)]
    acc = [l for l in L if 'ACCDEP' in l]
    slopes = []
    for l in acc:
        c = [int(x) for x in re.search(r'counts=\[([\d, ]+)\]', l).group(1).split(',')]
        slopes.append(round((c[-1] - c[0]) / 6, 2))   # X = 5, 8, 11
    ones = sum(1 for l in acc if re.search(r'hit: 0\*2 4\*\d+ ', l))
    term = [l for l in L if re.match(r'EV\d+ X=', l)]
    halts = [l for l in term if 'HALT' in l]
    print(f'{f[6:-4]:6s} events={len(evs):3d} accdep={len(acc):2d} ones-lists={ones:2d} slopes={slopes[:8]} '
          f'halt={"YES " + halts[0][:150] if halts else "no"} end={(term[0][:60] if term else "running/limit")}')
