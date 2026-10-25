"""Run the whole verification chain of this report on a machine (default: the main machine), for relatives.
  python relcheck.py MACHINE
1 blank -> K(1^11; 1; 2) (= B(5;[1]^12)); 2 outer rule grid; 3 K(0^11;0;b) -> J_b(1*,1,1,1;1;2) for b=1..6;
4 inner rule grids; 5 e1 borrow; 6 inner exhaustion J(0*,0,0,0;0;b) halts at 36b^2+636b+920 with 24B+6b+47 ones."""
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
M = sys.argv[1]
os.environ['TM9'] = M
sys.path.insert(0, str(HERE))
from dconf import build  # noqa: E402
from inner_start import inner_word  # noqa: E402
from exh_check import J  # noqa: E402
from kword import kword  # noqa: E402

TR = str(HERE / 'tr9b.exe')
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
tmp = HERE / '_rel_target.txt'


def run(args):
    return subprocess.run([TR, M] + args, capture_output=True, text=True, creationflags=LOW).stdout.strip().splitlines()


def match(word, head, state, target, maxs):
    tmp.write_text(target)
    out = run([word or '-', str(head), state, str(maxs), 'match', str(tmp)])
    return out[-1] if out else '?'


print('machine', M)
print('1 blank -> K(1^11;1;2):', match('', 0, 'A', kword([1] * 11, 1, 2), 10 ** 7))
for kind in ('outer', 'inner1', 'inner0'):
    r = subprocess.run([sys.executable, str(HERE / 'rulegrid.py'), kind, '1', '3', '2', '2', '4'], capture_output=True,
                       text=True).stdout.strip().splitlines()
    print('2/4 rule grid', r[-1], '(+%d mismatch lines)' % (len(r) - 1))
for b in range(1, 7):
    w = kword([0] * 11, 0, b)
    print(f'3 K(0^11;0;{b}) -> J_b inner start:', match(w, len(w), 'B', inner_word(b), 10 ** 9))
for b in range(0, 6):
    w = J(1, 1, [0, 0, 0], 0, b)
    print(f'5 e1 borrow b={b}:', match(w, len(w), 'B', J(1, 0, [2 * b + 2, 0, 0], 0, 0), 10 ** 8))
bad = 0
for b in range(0, 31):
    w = J(1, 0, [0, 0, 0], 0, b)
    pred = 36 * b * b + 636 * b + 920
    out = [x for x in run([w, str(len(w)), 'B', str(3 * pred + 1000), 'quiet']) if x[:4] in ('HALT', 'END ')]
    line = out[0] if out else '?'
    ok = line.startswith(f'HALT step {pred}:') and f'ones {24 + 47 + 6 * b},' in line
    if not ok:
        bad += 1
        if bad <= 3:
            print(f'6 exhaustion b={b}: DIFF', line[:100])
print('6 exhaustion b=0..30: %d differ from the main machine (halt step 36b^2+636b+920, ones 6b+71)' % bad)
