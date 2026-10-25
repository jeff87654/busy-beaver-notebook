"""Literal checks of the champion rules in the generality the follower uses (any a, any r, any left context C):
 R1 [C | m+3 | r] -> [C | m | 2r+6]            (m >= 0, any residue)
 R2 [C, X+3 | 1 | r] -> [C, X | 2r+7 | 0]
 R3 [C, Y+3, 1^k | 1 | r] -> [C, Y, 2r+7, 1^(k-1) | 1 | 0]   (k >= 1)
Each must be the NEXT K-moment (kst.exe). Contexts: random tokens 0..14, some 40..90, empty context."""
import random, subprocess, sys
MACH = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_0RG1LD_1RH1LG_1LC0RG_---0LH'
def D(m): return '10' * m + '1'
TAIL = '10101010'
sv = subprocess.Popen(['./kst.exe', MACH, 'G'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1,
                      creationflags=getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0))
def nxt(T):
    w = ''.join(D(t) for t in T) + TAIL
    sv.stdin.write(f'{w} {len(w)} G 2000000000\n'); sv.stdin.flush()
    o = sv.stdout.readline().split()
    return o if o[0] != 'K' else [int(x) for x in o[3:]]
random.seed(int(sys.argv[1]) if len(sys.argv) > 1 else 7)
def ctx():
    if random.random() < 0.1: return []
    return [random.choice(list(range(15)) + [random.randint(40, 90)]) for _ in range(random.randint(1, 5))]
bad = 0; n = 0
def chk(lab, T, E):
    global bad, n
    n += 1
    got = nxt(T)
    if got != E:
        bad += 1
        if bad < 30: print('FAIL', lab, T[-8:], 'expected', E[-8:], 'got', got[-10:] if isinstance(got, list) else got)
for i in range(int(sys.argv[2]) if len(sys.argv) > 2 else 600):
    C = ctx(); r = random.choice([random.randint(0, 40), random.randint(41, 400)])
    m = random.randint(0, 14)
    chk('R1', C + [m + 3, r], C + [m, 2 * r + 6])
    X = random.randint(0, 14)
    chk('R2', C + [X + 3, 1, r], C + [X, 2 * r + 7, 0])
    k = random.randint(1, 6)
    chk('R3', C + [X + 3] + [1] * k + [1, r], C + [X, 2 * r + 7] + [1] * (k - 1) + [1, 0])
print(n, 'checks', bad, 'failures')
