"""The record's D2 stage for every residue of the zero count k mod 5 (and mod 25): run the BB(9) record from
Kt(1^k ++ [2;4;21;4]) 1 (3b+2) 6 to its halt (I reading 1) and print the halting tape as tokens."""
import subprocess, os, sys
from cend import Kt, PAD
from snap import tokens, rle
TMP = os.path.join(os.environ.get('CLAUDE_JOB_DIR', '.'), 'tmp', 'rec9ext')
X = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'xsim2.exe')
REC = sys.argv[1] if len(sys.argv) > 1 else '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_0RG0RE_0LH---'
mf = os.path.join(TMP, 'd2c_m.txt'); open(mf, 'w').write(REC + '\n')
b = 7
for k in list(range(40, 50)) + [66, 91, 116]:
    t, h, s = Kt([1] * k + [2, 4, 21, 4], 1, 3 * b + 2, 6)
    cf = os.path.join(TMP, 'd2c.txt'); open(cf, 'w').write(f'{s} {h}\n{t}\n')
    o = subprocess.run([X, mf, cf, '3000000000', '-d'], capture_output=True, text=True).stdout.split()
    tape = o[-1].split('=')[1]; hh = int(o[-2].split('=')[1])
    print(k, k % 5, k % 25, o[1], o[2], o[3], o[4], '|', ' '.join(rle(tokens(tape, hh)))[:260], flush=True)
