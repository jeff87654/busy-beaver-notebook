"""Compare right-edge D-token histories of two machines from the same start (K(0^n;0;b) or J_B(...)).
  python v13/hcmp.py M1 M2 kind args MAXSTEPS   kind=K: n b ; kind=J: B c"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
from kword import kword  # noqa: E402
from exh_check import J  # noqa: E402

LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
m1, m2, kind = sys.argv[1], sys.argv[2], sys.argv[3]
a1, a2, mx = int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
w = kword([0] * a1, 0, a2) if kind == 'K' else J(a1, 0, [0, 0, 0], 0, a2)


def hist(m):
    out = subprocess.run([str(HERE / 'tr9run3.exe'), m, w, str(len(w)), 'B', str(mx), 'dshape', '100000'],
                         capture_output=True, text=True, creationflags=LOW).stdout.splitlines()
    t = [(l.split(' | ', 1)[0], l.split(' | ', 1)[1]) for l in out if l.startswith('S ')]
    e = [l for l in out if l.startswith('HALT') or l.startswith('END')]
    return t, e[0][:70] if e else '?'


h1, e1 = hist(m1)
h2, e2 = hist(m2)
n = 0
while n < min(len(h1), len(h2)) and h1[n][1] == h2[n][1]:
    n += 1
print(f'{n} common snapshots of {len(h1)} / {len(h2)}; ends: M1 {e1} | M2 {e2}')
for i in range(max(0, n - 2), min(n + 6, max(len(h1), len(h2)))):
    a = h1[i] if i < len(h1) else ('', '')
    b = h2[i] if i < len(h2) else ('', '')
    print(f'  {i:3d} M1 {a[0][:12]:>12} {a[1][:120]}')
    print(f'      M2 {b[0][:12]:>12} {b[1][:120]}')
