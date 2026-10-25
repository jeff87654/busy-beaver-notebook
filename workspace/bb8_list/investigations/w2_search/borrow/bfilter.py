"""bfilter.py TSV [--d 28]: from benum RS leaves, keep those whose prefix P keeps the borrowed digit d nearest:
  strict = P ends with d followed only by 1s;  loose = P contains d and nothing >= 3 after it."""
import idle  # noqa: F401  (Idle priority)

import sys, argparse
from ilib import expand
ap = argparse.ArgumentParser(); ap.add_argument('tsv', nargs='+'); ap.add_argument('--d', type=int, default=28)
a = ap.parse_args()
for f in a.tsv:
    for l in open(f):
        x = l.rstrip('\n').split('\t')
        if x[1] != 'RS': continue
        P = expand(x[3]) if x[3] else []
        if a.d not in P: continue
        j = len(P) - 1 - P[::-1].index(a.d)
        after = P[j + 1:]
        lvl = 'strict' if all(v == 1 for v in after) else ('loose' if all(v < 3 for v in after) else None)
        if lvl: print(lvl, x[0].replace('1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_', ''), 'P=', x[3], 'c=', x[4], 'z=', x[5], 'st=', x[2])
