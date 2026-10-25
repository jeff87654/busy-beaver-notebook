"""Quick classification of group-1/group-2 relatives.
  python v13/classify.py MACHINE  -> one summary block
Checks: (a) blank -> K(1^11;1;2); (b) K(0^11;0;b) -> J_b inner start (b=1,2); (c) inner exhaustion J_1(0*,0,0,0;0;c)
for c=0..3: halt step/ones vs the main machine's law; (d) token history from J_6(0*,0,0,0;0;0) compared with the
group-2 reference g (right-edge D-token snapshots, steps ignored) up to the end configuration; (e) the real end
configuration (B=6, digit exhausted, acc X=2,5) run to a halt; (f) transition usage along (a)-(d)."""
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
from kword import kword  # noqa: E402
from inner_start import inner_word  # noqa: E402
from exh_check import J  # noqa: E402
from tok2word import tok2word  # noqa: E402

M = sys.argv[1]
TR = str(HERE / 'tr9run3.exe')
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
G = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_0RH0RF_0RE0LG_0RF---'
tag = re.sub(r'[^A-Za-z0-9]', '', M[28:])


def run(m, args, timeout=None):
    return subprocess.run([TR, m] + args, capture_output=True, text=True, creationflags=LOW,
                          timeout=timeout).stdout.splitlines()


def match(word, head, st, target, mx):
    tf = HERE / 'v13' / f'_t_{tag}.txt'
    tf.write_text(target)
    out = run(M, [word or '-', str(head), st, str(mx), 'match', str(tf)])
    return out[-1][:40] if out else '?'


def hist(m, w, mx, n):
    out = run(m, [w, str(len(w)), 'B', str(mx), 'dshape', str(n)])
    toks = [l.split(' | ', 1)[1] for l in out if l.startswith('S ')]
    end = [l for l in out if l.startswith('HALT') or l.startswith('END')]
    return toks, (end[0][:50] if end else '?')


res = [f'== {M}']
res.append('a blank->K(1^11;1;2): ' + match('', 0, 'A', kword([1] * 11, 1, 2), 10 ** 7))
for b in (1, 2):
    w = kword([0] * 11, 0, b)
    res.append(f'b K(0^11;0;{b})->J_b: ' + match(w, len(w), 'B', inner_word(b), 10 ** 9))
inner = []
for c in range(4):
    w = J(1, 0, [0, 0, 0], 0, c)
    out = run(M, [w, str(len(w)), 'B', str(10 ** 8), 'quiet'])
    h = out[0]
    pred = 36 * c * c + 636 * c + 920
    inner.append(f'c={c}:' + (h.split(':')[0][5:] + '/ones ' + h.split('ones ')[1].split(',')[0]
                              if h.startswith('HALT') else 'no-halt') + f'(main {pred}/{71 + 6 * c})')
res.append('c inner exhaustion: ' + ' '.join(inner))
w = J(6, 0, [0, 0, 0], 0, 0)
mine, endm = hist(M, w, 60000000, 100000)
refp = HERE / 'v13' / 'ref_g.txt'
if not refp.exists():
    ref, _ = hist(G, w, 60000000, 100000)
    refp.write_text('\n'.join(ref))
ref = refp.read_text().split('\n')
n = 0
while n < min(len(mine), len(ref)) and mine[n] == ref[n]:
    n += 1
res.append(f'd history vs g from J_6(0*,0,0,0;0;0): {n} of {len(ref)} snapshots identical; end {endm}')
if n < len(mine) and n < len(ref):
    res.append('   first diff  mine: ' + mine[n][:150])
    res.append('                  g: ' + ref[n][:150])
s = (HERE / 'g2' / 'endtoks_B6.txt').read_text().strip()
for X in (2, 5):
    t = re.sub(r' 4 2\*2 (\d+) 1 2 ', f' 4 2*2 1 1 {X} ', s, count=1)
    w = tok2word(t)
    out = run(M, [w, str(len(w)), 'B', str(3 * 10 ** 8), 'quiet'])
    res.append(f'e end config X={X}: ' + out[0][:60])
print('\n'.join(res), flush=True)
