import fext, follow3 as F, subprocess, os
from cend import Kt, PAD
s = fext.d2_input()
T = os.path.join(os.environ['CLAUDE_JOB_DIR'], 'tmp', 'rec9ext')
REC = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_0RG0RE_0LH---'
for q, b in [(2, 4), (6, 9)]:
    R1 = (5 * q + 30) // 4
    w = F.word_of(F.inst(s, {'R1': R1, 'R2': 3 * b + 2}))
    t, h, st = Kt([1] * (5 * q + 11) + [2, 4, 21, 4], 1, 3 * b + 2, 6)
    k = t[PAD:h].lstrip('0')
    for name, word in (('follower', w), ('Kt', k)):
        fn = os.path.join(T, 'w.txt'); open(fn, 'w').write(word)
        r = subprocess.run([F.HYB, REC, fn, str(len(word)), 'B', '100000000', '-k', '0'], capture_output=True, text=True)
        print(q, b, name, r.stdout.strip().splitlines()[-1][:60])
