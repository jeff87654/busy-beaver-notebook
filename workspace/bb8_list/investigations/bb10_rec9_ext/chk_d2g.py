import fext, follow3 as F, subprocess, os
T = os.path.join(os.environ['CLAUDE_JOB_DIR'], 'tmp', 'rec9ext')
REC = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_0RG0RE_0LH---'
s = fext.d2_input()
for R1, R2 in [(10, 14), (210, 212), (215, 401)]:
    w = F.word_of(F.inst(s, {'R1': R1, 'R2': R2}))
    fn = os.path.join(T, 'w.txt'); open(fn, 'w').write(w)
    r = subprocess.run([F.HYB, REC, fn, str(len(w)), 'A', '2000000000', '-k', '0', '-q', 'A'], capture_output=True, text=True)
    print(R1, R2, 'follower/A', r.stdout.strip().splitlines()[-1][:100])
