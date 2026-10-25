"""Literal check of the champion rules R1-R3 with probe2.exe (one family step per probe), for a K-type template.
  python rulegrid.py outer|inner1|inner0 [BOUTER=1] [MAXLEN=3] [MAXD=2] [MAXA=2] [MAXB=4]
outer : K template  P=11, S=111001 (the BB(7) champion's family)
inner1: inner template, prefix = L(BOUTER) + (10)^8 0 1111 (10)^3 0 + D(2) D(5)   (first inner digit e1 = 1*)
inner0: same with D(2) D(2)                                                         (e1 = 0*)
Predicted step: a>0: (ds; a-1; 2b+2); a=0, last digit d>0: (ds,d-1; 2b+2; 0);
a=0, last nonzero digit d followed by k>=1 zeros: (.., d-1, 2b+2, 0^(k-1); 0; 0).  All-zero lists are skipped."""
import itertools
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dconf import build  # noqa: E402
from inner_start import lout  # noqa: E402

import os
M = os.environ.get('TM9', '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RI0LC_1RG1LD_0RH0RF_0RE0LG_---1LF')
PROBE = str(Path(__file__).resolve().parents[2] / 'neighbors' / 'probe2.exe')
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)


def predict(ds, a, b):
    if a > 0:
        return list(ds), a - 1, 2 * b + 2
    if ds and ds[-1] > 0:
        return list(ds[:-1]) + [ds[-1] - 1], 2 * b + 2, 0
    nz = [i for i, d in enumerate(ds) if d > 0]
    if not nz:
        return None
    j = nz[-1]
    k = len(ds) - j - 1
    return list(ds[:j]) + [ds[j] - 1, 2 * b + 2] + [0] * (k - 1), 0, 0


def main():
    kind = sys.argv[1]
    bo = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    maxlen, maxd, maxa, maxb = (int(x) for x in (sys.argv[3:7] + ['3', '2', '2', '4'][len(sys.argv[3:7]):]))
    if kind == 'outer':
        P, S = '11', '111001'
    else:
        e1 = '5' if kind == 'inner1' else '2'
        P = build([lout(bo), 'RAW:(10)^8 0', 'D:0,0,0,0', 'RAW:(10)^3 0', 'D:2,' + e1])
        S = '11111111001001'
    probes = []
    for n in range(0, maxlen + 1):
        for ds in itertools.product(range(maxd + 1), repeat=n):
            for a in range(maxa + 1):
                for b in range(maxb + 1):
                    if predict(ds, a, b) is None:
                        continue
                    probes.append((ds, a, b))
    bad = 0
    for i in range(0, len(probes), 40):
        chunk = probes[i:i + 40]
        args = [PROBE, M, 'R', 'B', P, '10', '1', '3', '1', '3', '2', S, '20000000']
        args += [','.join(map(str, ds)) + f';{a};{b}' for ds, a, b in chunk]
        out = subprocess.run(args, capture_output=True, text=True, creationflags=LOW).stdout.strip().splitlines()
        assert len(out) == len(chunk), out
        for (ds, a, b), line in zip(chunk, out):
            pd, pa, pb = predict(ds, a, b)
            exp = 'K(' + ','.join(map(str, pd)) + f'; {pa}; {pb})'
            got = line.split(' -> ')[1]
            if not got.startswith(exp + ' in'):
                bad += 1
                print('MISMATCH', line, 'expected', exp)
    print(f'{kind} BOUTER={bo}: {len(probes)} probes, {bad} mismatches')


if __name__ == '__main__':
    main()
