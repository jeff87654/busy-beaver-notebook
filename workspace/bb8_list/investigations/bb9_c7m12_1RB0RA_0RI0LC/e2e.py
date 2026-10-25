"""End-to-end literal runs of small inner-counter states to the halt; compare ones with 24B+6*b_f+47.
  python e2e.py   (cases: (e1*,e2,e3,e4; a; b) -> predicted b_f via the rules)"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from exh_check import J, M  # noqa: E402

LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)


def final_b(e, a, b):
    e = list(e)  # e[0] = e1*, rest normal; champion rules until all zero
    while True:
        if a > 0:
            if a > 60:
                return 10 ** 30  # astronomically large: the case is skipped
            b = (2 ** a) * (b + 2) - 2
            a = 0
            continue
        nz = [i for i, d in enumerate(e) if d > 0]
        if not nz:
            return b
        j = nz[-1]
        if j == len(e) - 1:
            e[j] -= 1
            a, b = 2 * b + 2, 0
        else:
            e[j] -= 1
            e[j + 1] = 2 * b + 2
            b = 0


cases = [((0, 0, 0, 1), 0, 0), ((0, 0, 0, 0), 3, 0), ((0, 0, 0, 0), 7, 0), ((0, 0, 1, 0), 0, 0)]
for bo in (1, 2):
    for e, a, b in cases:
        bf = final_b(e, a, b)
        if bf > 40000:
            print(f'B={bo} J{e};{a};{b}: predicted b_f={bf} too large, skipped')
            continue
        w = J(bo, e[0], list(e[1:]), a, b)
        out = subprocess.run([str(HERE / 'tr9b.exe'), M, w, str(len(w)), 'B', str(10 ** 12), 'quiet'],
                             capture_output=True, text=True, creationflags=LOW).stdout.strip().splitlines()
        ones = int(out[0].split('ones ')[1].split(',')[0])
        print(f'B={bo} J{e};{a};{b}: predicted b_f={bf}, {out[0][:60]} ; ones == 24B+6b_f+47: {ones == 24 * bo + 6 * bf + 47}',
              flush=True)
