"""Scan the inner exhaustion J(0*,0,0,0;0;b) for b in a range: halts at the predicted step 36b^2+636b+920?
  python exh_scan.py BOUTER B0 B1 [SLACK=2]   (runs each b up to SLACK * predicted steps)"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from exh_check import J, M, TR, LOW  # noqa: E402


def main():
    bo, b0, b1 = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    slack = float(sys.argv[4]) if len(sys.argv) > 4 else 2
    for b in range(b0, b1 + 1):
        pred = 36 * b * b + 636 * b + 920
        w = J(bo, 0, [0, 0, 0], 0, b)
        out = subprocess.run([TR, M, w, str(len(w)), 'B', str(int(pred * slack) + 1000), 'geo', '1e30'],
                             capture_output=True, text=True, creationflags=LOW).stdout.strip().splitlines()
        line = [x for x in out if x.startswith('HALT') or x.startswith('END')][0]
        ok = line.startswith(f'HALT step {pred}:')
        ones = int(line.split('ones ')[1].split(',')[0]) if 'ones' in line else -1
        print(b, 'OK' if ok else 'DIFF', line[:90], 'ones-formula', 24 * bo + 47 + 6 * b == ones, flush=True)


if __name__ == '__main__':
    main()
