"""Exact literal checks of the rules of 1RB1RH_0LC0LF_0RH1LD_0RE1LF_1RA1RD_0LG0LE_1LB1LF_1RF---
(C0 = 0RH variant of ../bb8_048631_1RB1RH0LC0LF; T, R, L1 and digit as there, RO/RE and Z0 changed).
Each start configuration is  0^inf X W E>0 0^inf  (head in E on the blank cell right of the word).
Run with no acceleration until the head first reaches a new rightmost cell in state E (or halts);
compare the full tape with the target and record the leftmost visited cell (X must not be visited).
"""
import random, json, sys
from lit import parse, MAIN, ST
TM = parse(MAIN)

def run(left, maxsteps=10**8):
    # left: list of cells (left to right); head at index len(left) reading 0, state E
    N = len(left)
    tape = {i: c for i, c in enumerate(left)}
    pos, q, steps, hi, lo = N, ST.index('E'), 0, N, N
    while steps < maxsteps:
        s = tape.get(pos, 0)
        e = TM[q][s]
        if e is None:
            return 'HALT', steps, tape, pos, q, lo
        w, d, q = e
        tape[pos] = w; pos += d; steps += 1
        lo = min(lo, pos)
        if pos > hi:
            hi = pos
            if ST[q] == 'E':
                return 'E', steps, tape, pos, q, lo
    return 'TIMEOUT', steps, tape, pos, q, lo

def word(tape, pos):
    ks = [k for k, v in tape.items() if v]
    lo = min(ks + [pos]); 
    return ''.join(str(tape.get(i, 0)) for i in range(lo, pos)), lo

def bits(s): return [int(c) for c in s]

def check(name, Xs, pat, tgt, halt_tgt=None):
    """pat, tgt: strings (the part right of X). X from Xs (strings). Returns failures."""
    fails = 0; steps_seen = []
    for X in Xs:
        left = bits(X + pat)
        res, steps, tape, pos, q, lo = run(left)
        cells = ''.join(str(tape.get(i, 0)) for i in range(min(tape) if tape else 0, max(list(tape) + [pos]) + 1))
        # tape relative to start: X occupies 0..len(X)-1
        if halt_tgt is not None:
            ok = res == 'HALT'
            if ok:
                full = ''.join(str(tape.get(i, 0)) for i in range(min(list(tape) + [0]), pos + 1))
                w = ''.join(str(tape.get(i, 0)) for i in range(min(list(tape) + [0]), pos))
                w = w.lstrip('0')
                ok = (X + halt_tgt[0]).lstrip('0') == w and tape.get(pos, 0) == halt_tgt[1] and ST[q] == 'H'
        else:
            ok = res == 'E'
            if ok:
                w = ''.join(str(tape.get(i, 0)) for i in range(min(list(tape) + [0]), pos))
                ok = w.lstrip('0') == (X + tgt).lstrip('0') and all(v == 0 for k, v in tape.items() if k >= pos)
        if ok and X:  # context cells never visited
            ok = lo >= len(X)
        if not ok:
            fails += 1
            print('FAIL', name, repr(X[-8:]), pat[:40], res, steps, lo)
        steps_seen.append(steps)
    return fails, steps_seen

random.seed(1)
def ctxs(n=3, lead=''):
    out = [lead + ''.join(random.choice('01') for _ in range(12)) for _ in range(n)]
    return out

results = {}
tot = 0
B = int(sys.argv[1]) if len(sys.argv) > 1 else 60
for b in range(0, B):
    # T: X 1 0 1 (10)^b -> X 1 (10)^(b+3)
    f, st = check('T', ctxs(), '101' + '10' * b, '1' + '10' * (b + 3)); tot += f
    results.setdefault('T', []).append((b, st[0]))
    # R: X 1 1 (10)^(b+1) -> X (10)^b 1 (10)^4
    f, st = check('R', ctxs(), '11' + '10' * (b + 1), '10' * b + '1' + '10' * 4); tot += f
    results.setdefault('R', []).append((b, st[0]))
    # L1: 0^inf 1 (10)^b -> 0^inf (10)^(b+3)
    f, st = check('L1', [''], '1' + '10' * b, '10' * (b + 3)); tot += f
    results.setdefault('L1', []).append((b, st[0]))
    # reset odd: 0^inf (10)^(2j+1) -> 0^inf 10 (1110)^j 11 (10)^2
    j = b
    f, st = check('RO', [''], '10' * (2 * j + 1), '10' + '1110' * j + '11' + '10' * 2); tot += f
    results.setdefault('RO', []).append((j, st[0]))
    # reset even: 0^inf (10)^(2j+2) -> halt at 0^inf 10 (1110)^(j+1) 11 [H1]
    f, st = check('RE', [''], '10' * (2 * j + 2), None, halt_tgt=('10' + '1110' * (j + 1) + '11', 1)); tot += f
    results.setdefault('RE', []).append((j, st[0]))
# digit rule, composite: X (1110)^(k+1) 11 (10)^n -> ... check by chaining single events? do direct:
def run_until_word(left, target, maxsteps=10**8):
    N = len(left); tape = {i: c for i, c in enumerate(left)}
    pos, q, steps, hi, lo = N, ST.index('E'), 0, N, N
    while steps < maxsteps:
        s = tape.get(pos, 0); e = TM[q][s]
        if e is None: return 'HALT', steps, lo
        w, d, q = e; tape[pos] = w; pos += d; steps += 1; lo = min(lo, pos)
        if pos > hi:
            hi = pos
            if ST[q] == 'E':
                w_ = ''.join(str(tape.get(i, 0)) for i in range(min(list(tape) + [0]), pos)).lstrip('0')
                if w_ == target.lstrip('0'): return 'OK', steps, lo
    return 'TIMEOUT', steps, lo
dig = []
for X in ['', '1', '10', '0110', '1010011']:
    for k in range(0, 3):
        for n in range(1, 12):
            left = bits(X + '1110' * (k + 1) + '11' + '10' * n)
            tgt = X + '1110' * k + '11' + '10' * (9 * n + 13)
            r, steps, lo = run_until_word(left, tgt)
            ok = r == 'OK' and lo >= len(X)
            if not ok:
                tot += 1; print('FAIL digit', X, k, n, r)
            dig.append((X, k, n, steps))
results['digit'] = dig
# Y(0,n) = 0^inf 10 11 (10)^n -> 0^inf (10)^(3n+7)
z0 = []
for n in range(1, 40):
    r, steps, lo = run_until_word(bits('10' + '11' + '10' * n), '10' * (3 * n + 7))
    if r != 'OK': tot += 1; print('FAIL Z0', n, r)
    z0.append((n, steps))
results['Z0'] = z0
print('total failures:', tot)
json.dump(results, open('check_rules.json', 'w'))
for k in ('T', 'R', 'L1', 'RO', 'RE'):
    xs = results[k]
    a = xs[1][1] - xs[0][1]; c = xs[0][1]
    lin = all(st == a * x + c for x, st in xs)
    print(k, xs[:4], 'steps = %d*x + %d exactly linear: %s' % (a, c, lin))
    if not lin: tot += 1
def D(n): return 120 * n * n + 400 * n + 344
def pre(n): return 12 * n * n + 70 * n + 101
bd = sum(1 for X, k, n, st in dig if st != D(n)); bz = sum(1 for n, st in z0 if st != pre(n))
print('digit: %d cases, %d with steps != D(n) = 120n^2+400n+344' % (len(dig), bd))
print('Y0 reset: %d cases, %d with steps != 12n^2+70n+101' % (len(z0), bz))
print('total failures incl. step formulas:', tot + bd + bz)
