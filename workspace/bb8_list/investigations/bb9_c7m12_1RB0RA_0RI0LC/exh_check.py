"""Literal checks around the inner list's exhaustion.
  python exh_check.py borrow BOUTER BMAX     : J(1*,0,0,0;0;b) reaches J(0*,2b+2,0,0;0;0)   (b = 0..BMAX)
  python exh_check.py exhaust BOUTER b1 b2.. : J(0*,0,0,0;0;b) -> halt; prints step, ones, final tape tokens"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dconf import build  # noqa: E402
from inner_start import lout  # noqa: E402

import os
M = os.environ.get('TM9', '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RI0LC_1RG1LD_0RH0RF_0RE0LG_---1LF')
HERE = Path(__file__).parent
TR = str(HERE / 'tr9b.exe')
S = 'RAW:1^8 00 1 00 1'
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)


def J(bo, e1, e234, a, b):
    return build([lout(bo), 'RAW:(10)^8 0', 'D:0,0,0,0', 'RAW:(10)^3 0',
                  'D:2,' + str(3 * e1 + 2) + ',' + ','.join(str(3 * e + 1) for e in e234) + f',{3 * a + 1}',
                  f'R:{3 * b + 2}', S])


def main():
    mode, bo = sys.argv[1], int(sys.argv[2])
    tmp = HERE / ('_exh_target_%d.txt' % bo)
    if mode == 'borrow':
        for b in range(int(sys.argv[3]) + 1):
            w = J(bo, 1, [0, 0, 0], 0, b)
            tmp.write_text(J(bo, 0, [2 * b + 2, 0, 0], 0, 0))
            out = subprocess.run([TR, M, w, str(len(w)), 'B', '10000000000', 'match', str(tmp)], capture_output=True,
                                 text=True, creationflags=LOW).stdout.strip().splitlines()
            print(f'b={b}:', out[-1] if out else '?')
    else:
        for b in map(int, sys.argv[3:]):
            w = J(bo, 0, [0, 0, 0], 0, b)
            out = subprocess.run([TR, M, w, str(len(w)), 'B', '100000000000', 'geo', '1e30'], capture_output=True,
                                 text=True, creationflags=LOW).stdout.strip().splitlines()
            line = [x for x in out if x.startswith('HALT') or x.startswith('END')]
            print(f'BOUTER={bo} b={b}:', line[0] if line else out[-2:], '| L-ones', w.count('1'))
            if len(sys.argv) <= 6:
                i = out.index(line[0])
                print('    ', out[i + 1][:300])


if __name__ == '__main__':
    main()
