"""Variant 11/12: K(0^11;0;b) -> Lambda(b) = 11 D4 D21 D4 D17 D4^(12b-12) D1 D34 D44 + tail (literal match).
  python v13/lam_check.py MACHINE b1,b2,..."""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
from kword import kword  # noqa: E402
from tok2word import tok2word  # noqa: E402

LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
M = sys.argv[1]
TAIL = '0*6 <1 00> 0*5 <1 00> 0*5 <1 00> 0*5 <1 00> 0*5 <1 00> 0*5 <1 00 1 00> 0'
for b in [int(x) for x in sys.argv[2].split(',')]:
    w = kword([0] * 11, 0, b)
    ones = ' '.join(['4'] * (12 * b - 12))
    target = tok2word(f'0*2 4 21 4 17 {ones} 1 34 44 {TAIL}')
    tf = HERE / 'v13' / f'_lam_{b}_{M[30:40]}.txt'
    tf.write_text(target)
    out = subprocess.run([str(HERE / 'tr9run3.exe'), M, w, str(len(w)), 'B', str(10 ** 10), 'match', str(tf)],
                         capture_output=True, text=True, creationflags=LOW).stdout.splitlines()
    print(f'b={b}: {out[-1][:60] if out else "?"}', flush=True)
    tf.unlink()
