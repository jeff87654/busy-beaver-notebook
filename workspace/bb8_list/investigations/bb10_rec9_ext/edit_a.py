"""Take the run of MACHINE from CONF to step N, replace the token D(OLD) (last occurrence left of the head) by D(NEW),
and run on (to halt or BUDGET), printing token snapshots.  Usage: python edit_a.py MACHINE CONF N OLD NEW BUDGET"""
import subprocess, sys, os, re
from snap import tokens, rle
X = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'xsim2.exe')
TMP = os.path.join(os.environ.get('CLAUDE_JOB_DIR', '.'), 'tmp', 'rec9ext')
m, conf, n, old, new, budget = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
mf = os.path.join(TMP, 'edit_m.txt'); open(mf, 'w').write(m + chr(10))
o = subprocess.run([X, mf, conf, str(n), '-d'], capture_output=True, text=True).stdout.split()
state = o[3]; tape = o[-1].split('=')[1]; h = int(o[-2].split('=')[1])
print('at', n, 'state', state, 'head', h, '|', ' '.join(rle(tokens(tape, h)))[:300])
pat = '1' + '01' * old + '1'          # D(old) followed by the next token's leading 1
i = tape.rfind(pat, 0, h)
assert i >= 0, 'token not found left of the head'
tape2 = tape[:i] + '1' + '01' * new + tape[i + 1 + 2 * old:]
h2 = h + 2 * (new - old)
print('edited', 'head', h2, '|', ' '.join(rle(tokens(tape2, h2)))[:300])
cf = os.path.join(TMP, 'edit_conf.txt'); open(cf, 'w').write(f'{state} {h2 + 50}\n' + '0' * 50 + tape2 + '0' * 50 + chr(10))
o = subprocess.run([X, mf, cf, budget, '-d'], capture_output=True, text=True).stdout.split()
tape3 = o[-1].split('=')[1]; h3 = int(o[-2].split('=')[1])
print('result', o[1], o[2], o[3], o[4], 'ones', o[5], '|', ' '.join(rle(tokens(tape3, h3)))[:400])
