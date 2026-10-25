"""Neighbourhoods of the champion-rule rebuilders, for grading with dlscan2.

The four parents follow the BB(7) champion's digit-list rules but rebuild the list when it is used up
instead of halting (dlscan2 grade NOBOUNDARY, R4 = KKKKK).  A neighbour whose rebuild halts for some
counter values (dlscan2 R4-SOME / HALT-SOME) would be Ackermann-level, like the BB(9) champion.

  python gen_nbrs.py RADIUS OUT.tsv [PARENTS.txt]   (default parents: the four rebuilders below)

Writes one row per distinct neighbour: machine, parents (comma-separated indices), changed transitions,
and `in_m8` = 1 if no change touches the champion's first eight transitions in first-use order
(A0 A1 B0 C0 C1 D0 D1 E1).  Such neighbours lie in the exhaustively enumerated and graded m8 subtree
(investigations/champ12_subtree/m8), so they serve as a consistency check; `in_m8` = 0 is new territory.
"""
from __future__ import annotations

import itertools
import sys

PARENTS = [
    '1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC0RH_1RG1RF',   # 30-digit start (m8)
    '1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_1LC0RH_1RG1RH',   # 30-digit start (m8)
    '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RG0LC_1RG1LD_0LH0RF_---1RE',   # 11-digit start (m12), never halts (Sonnet report)
    '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RG0LC_1RG1LD_0RH0RF_---1LE',   # 11-digit start (m12)
]
PREFIX = {'A0', 'A1', 'B0', 'C0', 'C1', 'D0', 'D1', 'E1'}
STATES = 'ABCDEFGH'
VALUES = ['---'] + [f'{w}{d}{q}' for w in '01' for d in 'LR' for q in STATES]


def cells(m):
    rows = m.split('_')
    return [rows[i][3 * s:3 * s + 3] for i in range(8) for s in range(2)]


def join(c):
    return '_'.join(c[2 * i] + c[2 * i + 1] for i in range(8))


def name(k):
    return f'{STATES[k // 2]}{k % 2}'


def main():
    radius, out = int(sys.argv[1]), sys.argv[2]
    parents = PARENTS if len(sys.argv) < 4 else open(sys.argv[3]).read().split()
    rows = {}
    for pi, p in enumerate(parents):
        base = cells(p)
        for r in range(1, radius + 1):
            for pos in itertools.combinations(range(16), r):
                for vals in itertools.product(*[[v for v in VALUES if v != base[k]] for k in pos]):
                    c = list(base)
                    for k, v in zip(pos, vals):
                        c[k] = v
                    m = join(c)
                    if m in parents:
                        continue
                    changed = ','.join(name(k) for k in pos)
                    in_m8 = int(not any(name(k) in PREFIX for k in pos))
                    if m in rows:
                        rows[m][0].add(pi)
                        rows[m][2] = max(rows[m][2], in_m8)
                    else:
                        rows[m] = [{pi}, changed, in_m8]
    with open(out, 'w') as f:
        for m, (ps, changed, in_m8) in rows.items():
            f.write(f'{m}\t{",".join(map(str, sorted(ps)))}\t{changed}\t{in_m8}\n')
    n_new = sum(1 for v in rows.values() if not v[2])
    print(f'{len(rows)} distinct neighbours (radius <= {radius}); {n_new} touch the prefix (new), '
          f'{len(rows) - n_new} inside the m8 subtree')


if __name__ == '__main__':
    main()
