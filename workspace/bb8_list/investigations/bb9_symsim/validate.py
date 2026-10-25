# validate.py: cross-check symsim against lit (literal) on random machines / M9 mutants.
#   python validate.py KIND N SEED [LITBUDGET] [SYMOPTS...]
# KIND: rand (random 2..6-state machines, one halt slot), m9mut (M9 with 1..3 random slot changes, random start)
import sys, random, subprocess, os, collections
D = os.path.dirname(os.path.abspath(__file__))
SYM, LIT = os.path.join(D, os.environ.get('SYMEXE', 'symsim.exe')), os.path.join(D, os.environ.get('LITEXE', 'lit.exe'))
kind, N, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
litb = int(sys.argv[4]) if len(sys.argv) > 4 else 2000000
symopts = sys.argv[5:]
random.seed(seed)
M9 = '1RB1RA_0LI1RC_0LD1LG_0RE1LD_1RF1RF_0RB0RA_1RA0LH_1LG1LH_---0LD'
def rslot(ns): return random.choice('01') + random.choice('LR') + chr(65 + random.randrange(ns))
def mk():
    if kind == 'rand':
        ns = random.randint(2, 6); sl = [rslot(ns) for _ in range(2 * ns)]
        sl[random.randrange(1, 2 * ns)] = '---'
        sl[0] = '1R' + sl[0][2]
        return '_'.join(sl[2*q] + sl[2*q+1] for q in range(ns)), 'A', ''
    if kind in ('m9mut', 'm9free', 'hold'):
        if kind == 'hold':
            sl = [x for x in HOLD[random.randrange(len(HOLD))] .replace('_', '')]
            sl = [''.join(sl[3*i:3*i+3]) for i in range(18)]
        else: sl = [M9[7*q+3*c:7*q+3*c+3] for q in range(9) for c in range(2)]
        for _ in range(random.randint(1, 3) if kind != 'hold' else 0):
            i = random.randrange(18) if kind == 'm9mut' else random.choice([2, 8, 10, 16, 17])
            sl[i] = random.choice([rslot(9)] * 8 + ['---'])
        if '---' not in sl: sl[random.randrange(18)] = '---'
        st = random.choice('ABCDEFGHI')
        tape = ''
        if random.random() < (0.5 if kind == 'm9mut' else 0.9):   # small structured start tape
            tape = random.choice(['', 'A> 0 0 111100', 'A> 0 0 111100^2', '10^2 1^3 A> 0', '10^3 H> 0 1^2', '10 1^2 B> 1 0 1^3',
                                  'BLK', 'BLK', 'BLK'])
            if tape == 'BLK':   # Ca j b (blk a z) with small values
                j, a, b = random.choice([(0, random.randint(0, 6), random.randint(0, 5)), (1, random.randint(0, 3), random.randint(0, 4)),
                                         (2, random.randint(0, 1), random.randint(0, 2)), (3, 0, random.randint(0, 2))])
                tape = ('10^%d ' % j if j else '') + ('1^%d ' % b if b else '') + 'A> 0 1^%d 0 ' % (a + 1) + random.choice(['', '1', '1^2', '1 0 1', '111100'])
                if random.random() < 0.4:   # k BLK blocks in a row: (0 1^(a+1))^k
                    k = random.randint(2, 4); j = random.randint(0, 1); a = random.randint(0, 1) if j else random.randint(0, 3); b = random.randint(0, 2)
                    tape = ('10^%d ' % j if j else '') + ('1^%d ' % b if b else '') + 'A> 0%s^%d 0 ' % ('1' * (a + 1), k) + random.choice(['', '1', '1^2'])
                st = 'A'
            elif tape and 'A>' in tape: tape = tape.replace('A>', st + '>')
        return '_'.join(sl[2*q] + sl[2*q+1] for q in range(9)), st, tape
HOLD = [l.split()[0] for l in open(os.path.join(D, '..', 'bb9_m9seed', 'grade1', 'in.txt'))] if kind == 'hold' else []
ms = [mk() for _ in range(N)]
inp = ''.join(f'{m} {s} {t}\n' for m, s, t in ms)
def run(cmd):
    if os.environ.get('PERM') and cmd[0] == SYM:   # one process per machine with a wall-clock cap (TIMEOUT = no verdict)
        res = []
        for m, s_, t_ in ms:
            try: o = subprocess.run(cmd, input=f'{m} {s_} {t_}\n', capture_output=True, text=True, timeout=int(os.environ['PERM'])).stdout.split('\n')
            except subprocess.TimeoutExpired: o = ['R %s %s TIMEOUT - sigma=? steps=?' % (m, s_), '']
            i = 0
            while i < len(o) and not o[i].startswith(('R ', 'L ')): i += 1
            res.append((o[i].split(), o[i + 1] if i + 1 < len(o) else '') if i < len(o) else (['R', m, s_, 'NOR', 'sigma=?', 'steps=?'], ''))
        return res
    out = subprocess.run(cmd, input=inp, capture_output=True, text=True).stdout.split('\n')
    res = []; i = 0
    while i < len(out):
        if out[i].startswith(('R ', 'L ')): res.append((out[i].split(), out[i + 1] if i + 1 < len(out) else '')); i += 2
        else: i += 1
    return res
L = run([LIT, str(litb)])
S = run([SYM, 'run', '--tape'] + symopts)
S0 = run([SYM, 'run', '--tape', '--noch'] + symopts)
assert len(L) == len(S) == len(S0) == N, (len(L), len(S), len(S0))
C = collections.Counter(); bad = []
for (m, st, tp), (l, lt), (s, stp), (s0, s0t) in zip(ms, L, S, S0):
    lo = l[3]; so = s[3]; s0o = s0[3]
    sig = lambda f: [x for x in f if x.startswith('sigma=')][0][6:]
    stp_ = lambda f: [x for x in f if x.startswith('steps=')][0][6:]
    key = f'lit={lo} sym={so} sym0={s0o}'
    C[key] += 1
    for name, so_, f, ft in (('ch', so, s, stp), ('noch', s0o, s0, s0t)):
        if lo == 'HALT':
            if so_ == 'HALT':
                if sig(f) != l[5] or ft != lt: bad.append((name, 'halt-mismatch', m, st, tp, l, f, lt, ft))
                elif stp_(f) != '?' and stp_(f) != l[4]: bad.append((name, 'steps-mismatch', m, st, tp, l[4], stp_(f)))
            elif so_ == 'CYCLE': bad.append((name, 'UNSOUND-cycle', m, st, tp, l, f))
        else:
            if so_ == 'HALT' and stp_(f) != '?' and int(stp_(f)) <= litb: bad.append((name, 'halt-early', m, st, tp, l, f))
for k, v in sorted(C.items()): print(f'{v:7d} {k}')
print('BAD', len(bad))
for b in bad[:20]: print(' ', b)
