"""Exact literal checks of the rules of 1RB1LE_0LC1RE_0RA0LD_1RA1LC_1LF0RC_1RG1LC_0LH1LG_1LB---.

Every start is  0^inf G>0 <word> 0^inf.  We run with no acceleration until the first later configuration
with state G reading 0 and blank tape to its left whose word matches the expected shape (or a halt),
require the exact predicted word, and (for cell rules with a context r) require that no cell of r was visited.

Cell rules (the Coq phase lemmas):
  R1 (m>=0): G>0 1^(3m+3) 0 1 r          -> G>0 1^(3m+9) r                 (next G0 config)
  R3 (j>=0): G>0 1^(6j+5) 0 r            -> G>0 111 (01)^(3j+4) 1 r         (next G0 config)
  Y4 (j>=0): G>0 1^(6j+4) 0^inf          -> G>0 111 (01)^(3j+3) 0^inf       (next G0 config)
  Y3 (j>=0): G>0 1^(6j+3) 0^inf          -> G>0 1^11 (01)^(3j+1) 11 0^inf   (2nd G0 config)
  Y1 (j>=0): G>0 1^(6j+1) 0^inf          -> G>0 1^11 (01)^(3j) 0^inf        (2nd G0 config)
Family rules, P(j,t,s) = G>0 1^(6j+5) (01)^t S_s with S_0 = 0^inf, S_1 = 11 0^inf; Y(n) = G>0 1^n 0^inf:
  Pstep  : P(j,t+1,s) -> P(3j+4,t,s)
  P00    : P(j,0,0)   -> Y(18j+28)            (= Y4 with j' = 3j+4)
  Y4f    : Y(6j+4)    -> Y(18j+21)            (= Y3 with j' = 3j+3)
  Y3f    : Y(6j+3)    -> P(1,3j+1,1)
  P01    : P(j,0,1)   -> P(1,3j+3,0)          (P(j,0,1) = Y(6j+7), Y1)
Also records exact step counts.
"""
import sys, random, json, re
from lit import parse, MAIN
T = parse(MAIN)
G = 6
random.seed(20260927)


def run(word, rlen, want, maxsteps=10**9):
    n = len(word)
    pad = 3 * n + 256
    tape = bytearray(pad) + bytearray(int(c) for c in word) + bytearray(pad)
    pos = pad - 1
    rstart = pad + n - rlen
    st = G
    steps = 0
    maxpos = pos; lo = pos
    while True:
        e = T[st][tape[pos]]
        if e is None:
            return ('HALT', steps, None, maxpos < rstart)
        w, d, q = e
        tape[pos] = w; pos += d; st = q; steps += 1
        if pos > maxpos: maxpos = pos
        if pos < lo: lo = pos
        if pos <= 0 or pos >= len(tape) - 1:
            return ('OUT', steps, None, False)
        if st == G and tape[pos] == 0 and not any(tape[lo:pos]):
            hi = len(tape) - 1
            while hi > pos and tape[hi] == 0: hi -= 1
            right = ''.join(map(str, tape[pos + 1:hi + 1]))
            if want(right):
                return ('G0', steps, right, maxpos < rstart)
        if steps > maxsteps:
            return ('LIMIT', steps, None, False)


def rtail():
    L = random.randint(0, 12)
    return ''.join(random.choice('01') for _ in range(L))


ANY = lambda w: True
FAM = lambda w: re.fullmatch(r'1+(01)*(11)?', w) is not None and re.fullmatch(r'(1*)', w) is None or re.fullmatch(r'1+', w) is not None


def P(j, t, s):
    return '1' * (6*j+5) + '01' * t + ('11' if s else '')


def Y(n):
    return '1' * n


def isP_or_Y(w):
    """a family word: 1^n (01)^t [11] with n = 6j+5 (P), or 1^n (Y)"""
    m = re.fullmatch(r'(1+)((?:01)*)(11)?', w)
    if not m:
        return False
    if m.group(2) == '' and m.group(3) is None:
        return True                           # Y(n)
    return len(m.group(1)) % 6 == 5 and m.group(2) != '' or (len(m.group(1)) % 6 == 5)


CELL = {
    'R1': (range(0, 60), lambda m: ('1' * (3*m+3) + '01', '1' * (3*m+9)), True, 1),
    'R3': (range(0, 40), lambda j: ('1' * (6*j+5) + '0', '111' + '01' * (3*j+4) + '1'), True, 1),
    'Y4': (range(0, 40), lambda j: ('1' * (6*j+4), '111' + '01' * (3*j+3)), False, 1),
    'Y3': (range(0, 40), lambda j: ('1' * (6*j+3), '1' * 11 + '01' * (3*j+1) + '11'), False, 2),
    'Y1': (range(0, 40), lambda j: ('1' * (6*j+1), '1' * 11 + '01' * (3*j)), False, 2),
}


def run_nth(word, rlen, k):
    """run to the k-th later left-edge G0 configuration"""
    cnt = [0]
    def want(w):
        cnt[0] += 1
        return cnt[0] == k
    return run(word, rlen, want)


res = {}
allok = True
for name, (rng, f, ctx, kth) in CELL.items():
    ok = bad = 0
    steps = {}
    for p in rng:
        for t in range(3 if ctx else 1):
            r = '' if t == 0 else rtail()
            lhs, rhs = f(p)
            kind, st, right, untouched = run_nth(lhs + r, len(r), kth)
            good = kind == "G0" and (untouched or not ctx) and right == (rhs + r).rstrip("0")
            if good:
                ok += 1
                if t == 0: steps[p] = st
            else:
                bad += 1
                print('FAIL', name, p, repr(r), kind, (right or '')[:80], untouched)
    res[name] = dict(ok=ok, bad=bad, steps=steps)
    allok &= bad == 0
    print('%-6s %5d ok %d fail   steps(first 5): %s' % (name, ok, bad, [steps.get(i) for i in list(rng)[:5]]))

# family rules: run to the first later family configuration (any P or Y word)
FAMRULES = []
for j in range(0, 12):
    for t in range(0, 4):
        for s in (0, 1):
            if 6 * (3*j+4) + 5 > 3000: continue
            FAMRULES.append(('Pstep', (j, t, s), P(j, t+1, s), P(3*j+4, t, s)))
    FAMRULES.append(('P00', (j,), P(j, 0, 0), Y(18*j+28)))
    FAMRULES.append(('P01', (j,), P(j, 0, 1), P(1, 3*j+3, 0)))
for j in range(0, 30):
    FAMRULES.append(('Y4f', (j,), Y(6*j+4), Y(18*j+21)))
    FAMRULES.append(('Y3f', (j,), Y(6*j+3), P(1, 3*j+1, 1)))


def famword(w):
    m = re.fullmatch(r'(1+)((?:01)*)(11)?', w)
    if not m:
        return False
    if m.group(2) == '' and m.group(3) is None:
        return True
    return len(m.group(1)) % 6 == 5 and not (m.group(2) == '' and m.group(3))


fam = {}
for name, key, start, pred in FAMRULES:
    kind, st, right, _ = run(start, 0, famword)
    good = kind == 'G0' and right == pred
    d = fam.setdefault(name, dict(ok=0, bad=0, steps={}))
    if good:
        d['ok'] += 1; d['steps'][','.join(map(str, key))] = st
    else:
        d['bad'] += 1; allok = False
        print('FAIL', name, key, kind, (right or '')[:100], 'pred', pred[:100])
for name, d in fam.items():
    print('%-6s %5d ok %d fail' % (name, d['ok'], d['bad']))
res.update(fam)
print('ALL OK' if allok else 'SOME FAILURES')
if len(sys.argv) > 1:
    json.dump(res, open(sys.argv[1], 'w'), indent=1)
