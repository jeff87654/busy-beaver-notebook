"""Literal checks (kst2.exe, next K-moment in EITHER frame) of the abstract rules used by ghf2.py, random left contexts:
 G: R1 [C|m+3|r]->[C|m|2r+6]; R2 [C,X+3|1|r]->[C,X|2r+7|0]; R3 [C,Y+3,1^k|1|r]->[C,Y,2r+7,1^(k-1)|1|0]
 B: R1B [C|m+3|r]->[C|m|2r+6]; R2B [C,X+3|0|r]->[C,X|r|6]"""
import random, subprocess, sys
from ghf2 import word, MACH
svs = {f: subprocess.Popen(['./kst2b.exe', MACH, f], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1,
                      creationflags=getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)) for f in 'GB'}
def nxt(fr, T):
    sv = svs[fr]; w = word(fr, T); sv.stdin.write(f'{w} {len(w)} {fr} 4000000000\n'); sv.stdin.flush()
    o = sv.stdout.readline().split()
    return (o[1], [int(x) for x in o[4:]]) if o[0] == 'K' else tuple(o)
random.seed(int(sys.argv[1])); N = int(sys.argv[2])
def ctx():
    if random.random() < 0.1: return []
    return [random.choice(list(range(15)) + [random.randint(40, 90)]) for _ in range(random.randint(1, 5))]
bad = n = 0
def chk(lab, fr, T, efr, E):
    global bad, n
    n += 1; got = nxt(fr, T)
    if got != (efr, E):
        bad += 1
        if bad < 30: print('FAIL', lab, fr, T[-7:], 'expected', efr, E[-7:], 'got', got[0], got[1][-9:] if len(got) > 1 else got)
for i in range(N):
    C = ctx(); r = random.choice([random.randint(0, 40), random.randint(41, 300)])
    m = random.randint(0, 14); X = random.randint(0, 14); k = random.randint(1, 6)
    chk('R1', 'G', C + [m + 3, r], 'G', C + [m, 2 * r + 6])
    chk('R2', 'G', C + [X + 3, 1, r], 'G', C + [X, 2 * r + 7, 0])
    chk('R3', 'G', C + [X + 3] + [1] * k + [1, r], 'G', C + [X, 2 * r + 7] + [1] * (k - 1) + [1, 0])
    chk('R1B', 'B', C + [m + 3, r], 'B', C + [m, 2 * r + 6])
    chk('R2B', 'B', C + [X + 3, 0, r], 'B', C + [X, r, 6])
print(n, 'checks', bad, 'failures')
