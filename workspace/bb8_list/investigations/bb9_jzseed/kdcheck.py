# kdcheck.py: one cascade jump (jz run --kd1) versus literal simulation: the predicted configuration
# (state D, head on the blank left of the word, same tape) must be visited by the literal run.
#   python kdcheck.py N SEED [STEPLIMIT]
import sys, random, subprocess, os
from jzlit import parse, CH, FW
D = os.path.dirname(os.path.abspath(__file__))
N, seed = int(sys.argv[1]), int(sys.argv[2]); LIM = int(sys.argv[3]) if len(sys.argv) > 3 else 3000000
random.seed(seed)
def rslot(): return random.choice('01') + random.choice('LR') + chr(65 + random.randrange(9))
cases = []
for _ in range(N):
    sl = [ (CH if random.random() < 0.5 else FW)[7*q+3*c:7*q+3*c+3] for q in range(9) for c in range(2)]
    for i in (8, 12, 14, 15, 16, 17):
        if random.random() < 0.5: sl[i] = random.choice([rslot()] * 5 + ['---'])
    m = '_'.join(sl[2*q] + sl[2*q+1] for q in range(9))
    while True:
        b = random.randint(0, 8); a = random.randint(0, 2)
        ds = [random.randint(0, 3)]
        r = random.random()
        if r < 0.3: ds += [0] * random.randint(1, 5) + [random.randint(1, 3)]          # deep digit: stop or small
        elif r < 0.6: ds += [random.choice([0, 1])] + [0] * random.randint(0, 3) + [random.choice([0, 1, 2])]
        else: ds += [random.choice([0, 0, 1, 2]) for _ in range(random.randint(0, 4))]
        # exact prediction (stop when B < 2j); accept only small outcomes
        B = b + 3 * a; ok = True
        for j, d in enumerate(ds):
            if d == 0: continue
            if B < 2 * j: break
            for _ in range(d):
                if j == 0: B = 3 * B + 7
                elif j == 1: B = (21 * 3 ** B - 7) // 2 if B < 40 else 10 ** 30
                elif j == 2 and B <= 2: B = 91
                else: B = 10 ** 30
            if B > 3000: ok = False; break
        if ok: break
    rep = ''
    if random.random() < 0.3:
        rep = ' %s^%d' % (random.choice(['0', '00', '0001', '00001']), random.randint(2, 70)) + random.choice(['', ' 0 1', ' 0 1^2'])
    t = 'D> 0 1^%d 0' % (b + 1) + (' 1^%d' % a if a else '') + ''.join(' 0' + (' 1^%d' % d if d else '') for d in ds) + rep
    cases.append((m, t))
inp = ''.join('%s D %s\n' % c for c in cases)
out = subprocess.run([os.path.join(D, 'jz.exe'), 'run', '--kd1'], input=inp, capture_output=True, text=True).stdout.strip().split('\n')
assert len(out) == len(cases)
def cells_of(t):
    s = ''; head = None
    for tok in t.split():
        if tok.endswith('>'): head = len(s); continue
        w, _, n = tok.partition('^'); s += w * (int(n) if n else 1)
    return s, head
stat = {'applied': 0, 'notapplied': 0, 'match': 0, 'nomatch': 0, 'skipbig': 0, 'symbolic': 0}
bad = []
for (m, t), o in zip(cases, out):
    f = o.split()
    if f[2] == '0': stat['notapplied'] += 1; continue
    stat['applied'] += 1
    if f[4] == '?' or f[4] == 'big': stat['symbolic'] += 1; continue
    q, hoff, pcells = f[4], int(f[5]), f[6]
    if len(pcells) > 3000: stat['skipbig'] += 1; continue
    T = parse(m); cells, head = cells_of(t)
    tape = {i: 1 for i, ch in enumerate(cells) if ch == '1'}; h = head; st = 3; found = False
    for step in range(LIM):
        if st == 3 and tape.get(h, 0) == 0 and tape and min(tape) > h:
            lo = min(tape); hi = max(tape)
            if h - lo == hoff and hi - lo + 1 == len(pcells):
                if ''.join('1' if tape.get(i, 0) else '0' for i in range(lo, hi + 1)) == pcells: found = True; break
        c = tape.get(h, 0); tr = T[(st, c)]
        if tr is None: break
        w, d, nq = tr
        if w: tape[h] = 1
        else: tape.pop(h, None)
        h += d; st = nq
    if found: stat['match'] += 1
    else: stat['nomatch'] += 1; bad.append((m, t, o[:200]))
print(stat)
for b in bad[:20]: print('NOMATCH', b)
