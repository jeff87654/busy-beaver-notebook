# hugetest.py: consistency of symsim's HUGE semantics against exact runs.
#   python hugetest.py exmax POOLFILE N SEED EXMAX_SMALL [symopts]    same machine/start: exact run (EXMAX 2^100) vs
#                                                                 symbolic run (exact values > EXMAX_SMALL become symbols)
#   python hugetest.py block POOLFILE N SEED [symopts]             start tapes with a block of length N: symbolic
#                                                                 (^H r, lower bound 10^5) vs exact 10^6+.. and 10^7+..
#                                                                 with the same residue mod MG
# Checks: an exact HALT must never meet a symbolic CYCLE and vice versa; when both halt, the symbolic sigma
# formula evaluated at the exact values must equal the exact sigma (when all its symbols are evaluable).
import sys, random, subprocess, os, re, collections
D = os.path.dirname(os.path.abspath(__file__))
SYM = os.path.join(D, os.environ.get('SYMEXE', 'symsim.exe'))
mode, pool, N, seed = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
random.seed(seed)
MG = 2520
lines = [l.split()[:2] for l in open(pool) if l.strip()]
sample = random.sample(lines, min(N, len(lines)))

def Wexact(j, b, cap=1 << 400):
    if j == 0: return b + 3
    if j == 1: return 3 * b + 5
    if j == 2: return (3 ** (b + 3) - 5) // 2 if b < 300 else None
    if j == 3: return 119 if b == 0 else None
    return None
def parse_lin(s, env):
    den = 1
    m = re.fullmatch(r'\((.*)\)/(\d+)', s)
    if m: s, den = m.group(1), int(m.group(2))
    tot = 0
    for sign, coef, var, const in re.findall(r'([+-]?)(?:(\d+)\*)?(?:(X\d+)|(\d+))', s):
        sg = -1 if sign == '-' else 1
        if var:
            v = env(var)
            if v is None: return None
            tot += sg * (int(coef) if coef else 1) * v
        else: tot += sg * int(const)
    assert tot % den == 0, (s, tot, den)
    return tot // den
def evaluator(descs, hval):
    memo = {}
    def env(x):
        if x in memo: return memo[x]
        d = descs.get(x)
        if d is None: return None
        v = None
        if d.startswith('E'): v = int(d[1:])
        elif d.startswith('H'): v = hval.get(x)
        elif d.startswith('W('):
            a, b = d[2:-1].rsplit(',', 1) if d.count(',') == 1 else (None, None)
            if a is not None:
                ja = parse_lin(a, env); ba = parse_lin(b, env)
                if ja is not None and ba is not None: v = Wexact(ja, ba)
        memo[x] = v; return v
    return env
def run(inp, opts):
    out = subprocess.run([SYM, 'run'] + opts, input=inp, capture_output=True, text=True).stdout.split('\n')
    res = []
    for l in out:
        if not l.startswith('R '): continue
        f = l.split()
        sig = [x for x in f if x.startswith('sigma=')][0][6:]
        descs = dict(re.findall(r'(X\d+)=(\S+?)\[r\d+\]', l))
        res.append((f[3], f[4], sig, descs))
    return res
symopts = sys.argv[6:] if mode == 'exmax' else sys.argv[5:]
C = collections.Counter(); bad = []
if mode == 'exmax':
    small = sys.argv[5]
    inp = ''.join(f'{m} {s}\n' for m, s in sample)
    E = run(inp, symopts); S = run(inp, symopts + ['--exmax', small])
    assert len(E) == len(S) == len(sample)
    for (m, s), e, y in zip(sample, E, S):
        C[f'exact={e[0]} sym={y[0]}'] += 1
        if y[0] == 'UNDECIDED' and os.environ.get('WHY'): C['  why ' + re.sub(r'\d+', '#', y[1])[:60]] += 1
        if {e[0], y[0]} == {'HALT', 'CYCLE'}: bad.append(('verdict', m, s, e[:3], y[:3]))
        if e[0] == y[0] == 'HALT':
            ve = parse_lin(e[2], evaluator(e[3], {})); vy = parse_lin(y[2], evaluator(y[3], {}))
            if ve is not None and vy is not None:
                C['sigma compared'] += 1
                if ve != vy: bad.append(('sigma', m, s, e[2], y[2], ve, vy))
            else: C['sigma not evaluable'] += 1
else:
    templ = ['1^N A> 0', '10^3 1^N A> 0 1^2', '10^2 1^N A> 0 1 0 1^3', '10^N H> 0 1^3', '10^5 1^7 A> 0 1^N',
             '1^N B> 0', '10 1^N H> 0 1^2', '01^N A> 0', '110^N C> 0 1', '10^4 1^N D> 0']
    jobs = []
    for m, s in sample:
        t = random.choice(templ); r = random.randrange(MG)
        n1 = 10**6 + (r - 10**6) % MG; n2 = 10**7 + (r - 10**7) % MG
        jobs.append((m, s, t, r, n1, n2))
    inpS = ''.join(f'{m} {s} {t.replace("^N", "^H" + str(r))}\n' for m, s, t, r, n1, n2 in jobs)
    inp1 = ''.join(f'{m} {s} {t.replace("^N", "^" + str(n1))}\n' for m, s, t, r, n1, n2 in jobs)
    inp2 = ''.join(f'{m} {s} {t.replace("^N", "^" + str(n2))}\n' for m, s, t, r, n1, n2 in jobs)
    S = run(inpS, symopts + ['--hlb', '100000']); E1 = run(inp1, symopts); E2 = run(inp2, symopts)
    assert len(S) == len(E1) == len(E2) == len(jobs)
    for (m, s, t, r, n1, n2), y, e1, e2 in zip(jobs, S, E1, E2):
        C[f'sym={y[0]} ex1={e1[0]} ex2={e2[0]}'] += 1
        for e, n in ((e1, n1), (e2, n2)):
            if {e[0], y[0]} == {'HALT', 'CYCLE'}: bad.append(('verdict', m, s, t, r, n, e[:3], y[:3]))
            if e[0] == y[0] == 'HALT':
                hid = [x for x, d in y[3].items() if d.startswith('H')]
                ve = parse_lin(e[2], evaluator(e[3], {}))
                vy = parse_lin(y[2], evaluator(y[3], {h: n for h in hid}))
                if ve is not None and vy is not None:
                    C['sigma compared'] += 1
                    if ve != vy: bad.append(('sigma', m, s, t, n, e[2], y[2], ve, vy))
                else: C['sigma not evaluable'] += 1
for k, v in sorted(C.items()): print(f'{v:7d} {k}')
print('BAD', len(bad))
for b in bad[:30]: print(' ', b)
