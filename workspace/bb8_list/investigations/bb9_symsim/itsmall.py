# itsmall.py: small-world literal checks of ITER rules at k >= 2 (and AFF/LIN for comparison).
#   python itsmall.py KIND N SEED CHUNK [SYMOPTS...]
# Generates machines exactly like validate.py (KIND rand / m9mut / hold), runs symsim --rulecheck --showproof on them in
# chunks, and tallies the RULECHECK lines per rule kind: tested / passed instances and the largest k checked literally
# (cell by cell, head-relative, sentinel-guarded; see ruleCheck in symsim.cpp).  Prints per-kind counts with k buckets.
import sys, random, subprocess, os, collections, re
D = os.path.dirname(os.path.abspath(__file__))
SYM = os.path.join(D, os.environ.get('SYMEXE', 'symsim_v14g.exe'))
kind, N, seed, chunk = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
symopts = sys.argv[5:]
# --- generator: copied verbatim from validate.py so that seeds give the same machines
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
        if random.random() < (0.5 if kind == 'm9mut' else 0.9):
            tape = random.choice(['', 'A> 0 0 111100', 'A> 0 0 111100^2', '10^2 1^3 A> 0', '10^3 H> 0 1^2', '10 1^2 B> 1 0 1^3',
                                  'BLK', 'BLK', 'BLK'])
            if tape == 'BLK':
                j, a, b = random.choice([(0, random.randint(0, 6), random.randint(0, 5)), (1, random.randint(0, 3), random.randint(0, 4)),
                                         (2, random.randint(0, 1), random.randint(0, 2)), (3, 0, random.randint(0, 2))])
                tape = ('10^%d ' % j if j else '') + ('1^%d ' % b if b else '') + 'A> 0 1^%d 0 ' % (a + 1) + random.choice(['', '1', '1^2', '1 0 1', '111100'])
                if random.random() < 0.4:
                    k = random.randint(2, 4); j = random.randint(0, 1); a = random.randint(0, 1) if j else random.randint(0, 3); b = random.randint(0, 2)
                    tape = ('10^%d ' % j if j else '') + ('1^%d ' % b if b else '') + 'A> 0%s^%d 0 ' % ('1' * (a + 1), k) + random.choice(['', '1', '1^2'])
                st = 'A'
            elif tape and 'A>' in tape: tape = tape.replace('A>', st + '>')
        return '_'.join(sl[2*q] + sl[2*q+1] for q in range(9)), st, tape
HOLD = [l.split()[0] for l in open(os.path.join(D, '..', 'bb9_m9seed', 'grade1', 'in.txt'))] if kind == 'hold' else []
ms = [mk() for _ in range(N)]
# --- run
C = collections.Counter(); fails = []; rows = collections.Counter()
pat = re.compile(r'^RULECHECK (ITER|AFF|LIN) tested=(\d+) passed=(\d+) maxk=(\d+)')
for i in range(0, N, chunk):
    part = ms[i:i + chunk]
    inp = ''.join(f'{m} {s} {t}\n' for m, s, t in part)
    try:
        p = subprocess.run([SYM, 'run', '--tape', '--rulecheck', '--showproof'] + symopts, input=inp, capture_output=True, text=True, timeout=3600)
        err, out = p.stderr, p.stdout
    except subprocess.TimeoutExpired as e:
        err = (e.stderr or b'').decode() if isinstance(e.stderr, bytes) else (e.stderr or ''); out = ''
        C['chunk-timeout'] += 1
    for ln in err.split('\n'):
        m = pat.match(ln)
        if m:
            k, t, ps, mk_ = m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4))
            if t == 0: C[(k, 'untestable')] += 1
            elif ps < t: C[(k, 'FAIL')] += 1
            else:
                b = 'k>=4' if mk_ >= 4 else 'k=%d' % mk_
                C[(k, 'PASS', b)] += 1
        elif ln.startswith('RULECHECK-FAIL'): fails.append(ln[:300])
    for ln in out.split('\n'):
        if ln.startswith('R '):
            f = ln.split(); rows[f[3]] += 1
            it = [x for x in f if x.startswith('it=')]
            if it and it[0] != 'it=0': rows['uses-ITER'] += 1
    print(f'.. {min(i + chunk, N)}/{N}', file=sys.stderr, flush=True)
for k in sorted(C, key=str): print(f'{C[k]:7d} {k}')
print('rows', dict(rows))
print('FAILS', len(fails))
for f in fails[:20]: print(' ', f)
