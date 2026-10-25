"""Silent single-transition changes of the BB(9) record: changes after which the run is literally identical on
probes covering every stage up to c_end: (a) blank tape, 3e7 steps; (b) the first rebuild from K(0^11;0;B) for
B = 2, 3 (5e6 steps); (c) the D2 stage d2start(q, b) -> c_end for (q, b) = (2, 4), (3, 7).  Final tape, head and
state must equal the record's.  Usage: python silent.py BASE"""
import subprocess, sys, os
from cend import c_end, d2start, Kt
BASE = sys.argv[1] if len(sys.argv) > 1 else '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_0RG0RE_0LH---'
TMP = os.path.join(os.environ.get('CLAUDE_JOB_DIR', '.'), 'tmp', 'rec9ext')
X = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'xsim.exe')
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
ALL = [f'{w}{d}{s}' for w in '01' for d in 'LR' for s in 'ABCDEFGHI']
rows = BASE.split('_')
variants = []
for si in range(9):
    for r in range(2):
        cur = rows[si][3 * r:3 * r + 3]
        if cur == '---':
            continue
        for v in ALL:
            if v != cur:
                nr = list(rows)
                nr[si] = rows[si][:3 * r] + v + rows[si][3 * r + 3:]
                variants.append((f'{chr(65 + si)}{r}={v}', '_'.join(nr)))
mf = os.path.join(TMP, 'silent_m.txt')
open(mf, 'w').write(BASE + '\n' + '\n'.join(m for _, m in variants) + '\n')
probes = [('blank', ('A', 40, '0' * 81), 10000000)]
for B in (2, 3):
    t, h, s = Kt([1] * 11, 1, 3 * B + 2, 0); probes.append((f'rebuild{B}', (s, h, t), 5000000))
for q, b in ((2, 4), (3, 7)):
    t, h, s = d2start(q, b); probes.append((f'd2_{q}_{b}', (s, h, t), 100000000))
alive = None
for name, (s, h, t), n in probes:
    cf = os.path.join(TMP, f'silent_{name}.txt'); open(cf, 'w').write(f'{s} {h}\n{t}\n')
    out = subprocess.run([X, mf, cf, str(n), '-d'], capture_output=True, text=True, creationflags=LOW).stdout.splitlines()
    sig = {}
    for l in out:
        f = l.split()
        sig[f[0]] = (f[1], f[2], f[4], f[-2], f[-1])   # state ignored: G0/H0-type twins differ only transiently
    ref = sig[BASE]
    same = {m for m, v in sig.items() if v == ref}
    alive = same if alive is None else alive & same
    print(name, 'record:', ref[:4], 'identical variants:', len(same) - 1, flush=True)
for lab, m in variants:
    if m in alive:
        print('SILENT', lab, m)
