"""Literal checks (kst3.exe: next G-frame K-moment, gap-aware) of the champion rules in contexts containing gaps 0^k
(k >= 2) and arbitrary tokens, including a gap immediately left of the active token:
 R1 [C|m+3|r]->[C|m|2r+6]; R2 [C,X+3|1|r]->[C,X|2r+7|0]; R3 [C,Y+3,1^k|1|r]->[C,Y,2r+7,1^(k-1)|1|0]"""
import random, subprocess, sys
MACH = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_0RG1LD_1RH1LG_1LC0RG_---0LH'
def D(m): return '0' * (-m) if m < 0 else '10' * m + '1'
sv = subprocess.Popen(['./kst3.exe', MACH], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1,
                      creationflags=getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0))
def nxt(T):
    w = ''.join(D(t) for t in T) + '10101010'
    sv.stdin.write(f'{w} {len(w)} G 4000000000\n'); sv.stdin.flush()
    o = sv.stdout.readline().split()
    return [int(x) for x in o[3:]] if o[0] == 'K' else o
random.seed(int(sys.argv[1])); N = int(sys.argv[2])
def ctx():
    C = []
    for _ in range(random.randint(1, 5)):
        C.append(random.choice(list(range(15)) + [random.randint(40, 90)]))
        if random.random() < 0.4: C.append(-random.randint(2, 5))
    if C[0] < 0: C.insert(0, 3)
    if random.random() < 0.5 and C[-1] >= 0: C.append(-random.randint(2, 4))   # gap right before the active part
    return C
bad = n = 0
def chk(lab, T, E):
    global bad, n
    n += 1; got = nxt(T)
    if got != E:
        bad += 1
        if bad < 25: print('FAIL', lab, T[-9:], 'expected', E[-9:], 'got', got[-11:] if isinstance(got, list) else got)
for i in range(N):
    C = ctx(); r = random.choice([random.randint(0, 40), random.randint(41, 300)])
    m = random.randint(0, 14); X = random.randint(0, 14); k = random.randint(1, 6)
    chk('R1', C + [m + 3, r], C + [m, 2 * r + 6])
    chk('R2', C + [X + 3, 1, r], C + [X, 2 * r + 7, 0])
    chk('R3', C + [X + 3] + [1] * k + [1, r], C + [X, 2 * r + 7] + [1] * (k - 1) + [1, 0])
print(n, 'checks', bad, 'failures')
