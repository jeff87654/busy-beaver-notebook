"""R4 over a grid of (zero digits n, counter b) for machines with a champion-type dlscan2 fit.

dlscan2 probes R4 only on the empty list K(; 0; b).  In a real run the list is all zeros when it is used
up, K(0^n; 0; b) with n large, and the finale may loop over those zero digits (champ35's FIN does), so
the outcome can depend on n as well.  A machine that halts for some (n, b) and rebuilds for others is
the BB(9)-champion pattern.

  python r4grid.py GRADED.tsv [NMAX=6] [BMAX=8] [CAP=5000000]

GRADED.tsv: rows with columns machine ... grade template ... (header names `machine`, `grade`,
`template`); rows with grade '-' or TIMEOUT are skipped.  Prints, per machine, one line per n with one
letter per b: H = halts, K = reaches a family configuration (rebuild; lowercase k if the new list is
not longer than before), T = neither within CAP steps.
"""
from __future__ import annotations

import re
import sys

from usage_phases import Tmpl, parse_tm, run


def tmpl_from(s):
    m = re.match(r'([LR]),([A-H]),P=([01-]*),u=([01]+),s=([01]+),d=(\d+)d\+(\d+),b=(\d+)b\+(\d+),S=([01-]*)$', s)
    if not m:
        return None, None
    o, q, P, u, sp, al, be, alB, beB, S = m.groups()
    return o, Tmpl(q, '' if P == '-' else P, u, sp, int(al), int(be), int(alB), int(beB), '' if S == '-' else S)


def mirror(m):
    return '_'.join(''.join(t if t == '---' else t[0] + {'L': 'R', 'R': 'L'}[t[1]] + t[2]
                            for t in (row[:3], row[3:])) for row in m.split('_'))


def grid(m, tstr, nmax, bmax, cap):
    o, T = tmpl_from(tstr)
    if T is None:
        return None
    tm = parse_tm(mirror(m) if o == 'L' else m)
    lines, letters = [], set()
    for n in range(nmax + 1):
        row = ''
        for b in range(bmax + 1):
            out, st, use, k = run(tm, T, T.build((0,) * n, 0, b), stop_any=True, cap=cap)
            if out == 'HALT':
                c = 'H'
            elif out == 'FAMILY':
                c = 'K' if len(k[0]) > n else 'k'
            else:
                c = 'T'
            row += c
            letters.add(c)
        lines.append(row)
    return lines, letters


def main():
    path = sys.argv[1]
    nmax = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    bmax = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    cap = int(sys.argv[4]) if len(sys.argv) > 4 else 5_000_000
    rows = open(path).read().splitlines()
    head = rows[0].split('\t')
    im, ig, it = head.index('machine'), head.index('grade'), head.index('template')
    for line in rows[1:]:
        f = line.split('\t')
        if f[ig] in ('-', 'TIMEOUT') or f[it] == '-':
            continue
        r = grid(f[im], f[it], nmax, bmax, cap)
        if r is None:
            print(f'{f[im]}  {f[ig]:<10} template not parsed: {f[it]}')
            continue
        lines, letters = r
        mixed = 'H' in letters and len(letters) > 1
        flag = 'MIXED' if mixed else ('ALL-HALT' if letters == {'H'} else 'NO-HALT')
        print(f'{f[im]}  {f[ig]:<10} {flag:<8} ' + ' '.join(f'n{n}:{s}' for n, s in enumerate(lines)), flush=True)


if __name__ == '__main__':
    main()
