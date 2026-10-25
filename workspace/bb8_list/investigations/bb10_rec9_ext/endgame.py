"""Endgame probe: every machine of a list from E(k, a, R, t) = D(0)^2 D(4) D(21) D(2) D(1)^k D(a) D(R) tail(t),
state A at the right end (follower phase).  Reports halts (and ones), and growth of the "11"-pair count (a
length-expanding rebuild shows as pairs >> pairs0).  Usage: python endgame.py MACHFILE OUT.tsv [budget]"""
import subprocess, sys, os
import follow3 as F
from follow3 import Aff, A
TMP = os.path.join(os.environ.get('CLAUDE_JOB_DIR', '.'), 'tmp', 'rec9ext')
X = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'xsim2.exe')
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
budget = sys.argv[3] if len(sys.argv) > 3 else '300000000'
one, two = A(1), A(2)


def cfg(k, a, R, t):
    tail = [('D', A(0), A(6)), ('B', (('R', ('1', one), one), ('R', ('0', two), one), ('D', A(0), A(5))), A(t)),
            ('R', ('1', one), one), ('R', ('0', two), one), ('R', ('1', one), one), ('R', ('0', two), one)]
    sym = [('D', A(0), A(2)), ('D', A(4), one), ('D', A(21), one), ('D', A(2), one)] + \
          ([('D', one, A(k))] if k else []) + [('D', A(a), one), ('D', A(R), one)] + tail
    return F.word_of(F.inst(sym, {}))


pts = [(0, 3, 200, 7), (0, 3, 203, 9), (0, 1, 200, 7), (0, 2, 200, 7), (0, 0, 200, 7), (2, 1, 200, 7), (1, 1, 203, 8)]
out = open(sys.argv[2], 'w')
for k, a, R, t in pts:
    w = cfg(k, a, R, t)
    cf = os.path.join(TMP, f'eg_{k}_{a}_{R}_{t}.txt')
    open(cf, 'w').write(f'A {len(w)}\n{w}\n')
    res = subprocess.run([X, sys.argv[1], cf, budget, '-p'], capture_output=True, text=True, creationflags=LOW).stdout
    for line in res.splitlines():
        f = line.split()
        out.write(f'{f[0]}\t{k},{a},{R},{t}\t' + ' '.join(f[1:]) + '\n')
    out.flush()
    print('done', k, a, R, t, flush=True)
