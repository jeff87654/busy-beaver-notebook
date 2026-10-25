"""Inner exhaustion J(0*,0,0,0;0;b) -> halt for relatives: fit steps and ones over b = 0..60."""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from exh_check import J  # noqa: E402

LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
for m in sys.argv[1:]:
    rows = []
    for b in range(0, 61):
        w = J(1, 0, [0, 0, 0], 0, b)
        out = subprocess.run([str(HERE / 'tr9b.exe'), m, w, str(len(w)), 'B', str(10 ** 9), 'quiet'], capture_output=True,
                             text=True, creationflags=LOW).stdout.strip().splitlines()[0]
        if not out.startswith('HALT'):
            rows.append((b, None, None))
            continue
        rows.append((b, int(out.split('step ')[1].split(':')[0]), int(out.split('ones ')[1].split(',')[0])))
    halts = [r for r in rows if r[1] is not None]
    s0, s1, s2 = (halts[i][1] for i in range(3))
    c2 = (s2 - 2 * s1 + s0) // 2
    c1 = s1 - s0 - c2
    okstep = all(r[1] == c2 * r[0] ** 2 + c1 * r[0] + s0 for r in halts)
    okones = all(r[2] == 6 * r[0] + halts[0][2] for r in halts)
    print(m, f'halts {len(halts)}/61; steps = {c2}b^2+{c1}b+{s0} for all: {okstep}; ones = 6b+{halts[0][2]} (B=1) for all: {okones}')
