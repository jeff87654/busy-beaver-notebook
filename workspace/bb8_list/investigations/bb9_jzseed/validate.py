# validate.py: cross-check jz.exe (with and without the cascade accelerator) against lit.exe (literal simulation).
#   python validate.py KIND N SEED [LITBUDGET] [JZOPTS...]
# KIND: free  (champion core 12 slots + random E0 G0 H0 H1 I0 I1, random start, blank or Kd start tape)
#       mut   (champion or fw2 in champion labels with 1..3 random slot changes, random start, blank or Kd tape)
#       rand  (random 2..7-state machines, one halt slot, blank tape)
# BAD = a contradiction (literal halt vs jz CYCLE, or different sigma/tape at a common halt).
import sys, random, subprocess, os, collections
D = os.path.dirname(os.path.abspath(__file__))
JZ = os.path.join(D, os.environ.get('JZEXE', 'jz.exe')); LIT = os.path.join(D, 'lit.exe')
kind, N, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
litb = int(sys.argv[4]) if len(sys.argv) > 4 else 2000000
jzopts = sys.argv[5:]
random.seed(seed)
CH = '1RB1RA_0LC0LF_0RD1LC_1RA1RG_1RZ0RA_1LB1LF_1LH1RE_0LI1LH_1LB0LH'
FW = '1RB1RA_0LC0LF_0RD1LC_1RA1RG_1RH0RA_1LB1LF_1RZ1RE_1LI1LI_0RE0LH'
FREE = [8, 12, 14, 15, 16, 17]          # E0 G0 H0 H1 I0 I1
def slots(m): return [m[7*q+3*c:7*q+3*c+3] for q in range(len(m.split('_'))) for c in range(2)]
def join(sl): return '_'.join(sl[2*q] + sl[2*q+1] for q in range(len(sl) // 2))
def rslot(ns): return random.choice('01') + random.choice('LR') + chr(65 + random.randrange(ns))
def kdtape():
    b = random.randint(0, 12); a = random.randint(0, 3)
    ds = [random.choice([0, 0, 1, 1, 2, 3, random.randint(0, 9)]) for _ in range(random.randint(0, 7))]
    t = 'D> 0 1^%d 0' % (b + 1) + (' 1^%d' % a if a else '')
    for d in ds: t += ' 0' + (' 1^%d' % d if d else '')
    return t
def mk():
    if kind == 'rand':
        ns = random.randint(2, 7); sl = [rslot(ns) for _ in range(2 * ns)]
        sl[random.randrange(1, 2 * ns)] = '---'; sl[0] = '1R' + sl[0][2]
        return join(sl), 'A', ''
    sl = slots(CH if (kind == 'free' or random.random() < 0.5) else FW)
    if kind == 'free':
        for i in FREE: sl[i] = random.choice([rslot(9)] * 6 + ['---'])
    else:
        for _ in range(random.randint(1, 3)): sl[random.randrange(18)] = random.choice([rslot(9)] * 8 + ['---'])
    if '---' not in sl: sl[random.choice(FREE)] = '---'
    st = random.choice('ABCDEFGHI'); tape = ''
    if random.random() < 0.4: tape = kdtape(); st = 'D'
    return join(sl), st, tape
ms = [mk() for _ in range(N)]
inp = ''.join(f'{m} {s} {t}\n' for m, s, t in ms)
def run(cmd):
    out = subprocess.run(cmd, input=inp, capture_output=True, text=True).stdout.split('\n')
    res = []; i = 0
    while i < len(out):
        if out[i].startswith(('R ', 'L ')): res.append((out[i].split(), out[i + 1] if i + 1 < len(out) else '')); i += 2
        else: i += 1
    return res
L = run([LIT, str(litb)])
S = run([JZ, 'run', '--tape'] + jzopts)
S0 = run([JZ, 'run', '--tape', '--noch'] + jzopts)
assert len(L) == len(S) == len(S0) == N, (len(L), len(S), len(S0))
C = collections.Counter(); bad = []
def sig(f): return [x for x in f if x.startswith('sigma=')][0][6:]
for (m, st, tp), (l, lt), (s, stp), (s0, s0t) in zip(ms, L, S, S0):
    for tag, (r, rt) in (('acc', (s, stp)), ('noacc', (s0, s0t))):
        v = r[3]
        if l[3] == 'HALT':
            if v == 'HALT':
                if sig(r) != l[5]: bad.append((tag, 'sigma', m, st, tp, l[5], sig(r)))
                elif rt.startswith('TAPE ') and rt.split()[1] not in ('?', 'big') and rt != lt: bad.append((tag, 'tape', m, st, tp, lt[:80], rt[:80]))
                else: C[tag + ' halt-match'] += 1
                if tag == 'acc' and 'kd=0' not in ' '.join(r): C['acc halt-match with cascade'] += 1
            elif v == 'CYCLE': bad.append((tag, 'cycle-vs-halt', m, st, tp, l[4], r[4]))
            else: C[tag + ' lit-halt jz-' + v] += 1
        else:
            if v == 'HALT': C[tag + ' jz-halt lit-budget'] += 1
            else: C[tag + ' lit-budget jz-' + v] += 1
for k in sorted(C): print(k, C[k])
print('BAD', len(bad))
for b in bad[:30]: print('BAD', b)
