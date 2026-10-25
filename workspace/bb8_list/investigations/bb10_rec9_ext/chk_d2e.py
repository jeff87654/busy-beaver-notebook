import fext, follow3 as F, subprocess, os
from cend import Kt, PAD
s = fext.d2_input()
T = os.path.join(os.environ['CLAUDE_JOB_DIR'], 'tmp', 'rec9ext')
REC = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_0RG0RE_0LH---'
for R1, R2 in [(10, 14), (210, 212), (215, 401)]:
    w = F.word_of(F.inst(s, {'R1': R1, 'R2': R2}))
    fn = os.path.join(T, 'w.txt'); open(fn, 'w').write(w)
    r = subprocess.run([F.HYB, REC, fn, str(len(w)), 'B', '2000000000', '-k', '0'], capture_output=True, text=True)
    print(R1, R2, 'follower', r.stdout.strip().splitlines()[-1][:100])
    if (4 * R1 - 30) % 5 == 0 and (R2 - 2) % 3 == 0:
        q = (4 * R1 - 30) // 5
        t, h, st = Kt([1] * (5 * q + 11) + [2, 4, 21, 4], 1, R2, 6)
        k = t[PAD:h].lstrip('0')
        fn = os.path.join(T, 'w.txt'); open(fn, 'w').write(k)
        r = subprocess.run([F.HYB, REC, fn, str(len(k)), 'B', '2000000000', '-k', '0'], capture_output=True, text=True)
        print(R1, R2, 'Kt', r.stdout.strip().splitlines()[-1][:100])
