"""Exact literal checks (no acceleration) of the rules of 1RB0LC_0RC0RF_0RD0RH_1LE---_0LF1LG_1RD1LA_1RC1LA_0LF0LA.

Configurations: 0^inf X W 0 0 D> 0^inf (head in state D on the blank right edge, two blanks behind it).
Phase rules (X arbitrary, must never be visited):
  R1  : X 0 1^(3m+1)  ->  X 1^(3m+6)
  R0o : X 0 1^(6i+3)  ->  X 1 (10)^(3i+2) 1
Top rules (X = 0^inf):
  T1  : 1^(6i+4)  ->  1 (10)^(3i+5) 1
  T2  : 1^(6j+2)  ->  1 (10)^(3j+1) 11 (10)^2 1
Family (X = 0^inf):  Cc a k = 1 (10)^a 11 (10)^k 1,  Dc a i = 1 (10)^a 1^(6i+3)
  C_D   : Cc a k     -> Dc a k
  Dstep : Dc (a+1) i -> Dc a (3i+2)
  Dtop  : Dc 0 i     -> Dc (9i+16) 2
Each run starts at the left-hand configuration and stops at the first later configuration whose whole tape,
head position and state equal the right-hand configuration (same left alignment of W).  It must not halt,
and for arbitrary X no cell of X may be visited.  For R1 and R0o the target must also be the FIRST later
right-edge configuration (state D on a blank cell, blank to the right, two blanks behind).
Also documented: X 0 1^(3m+2) with X ending in 1 halts (D1), and Dc/Cc never produce that situation.
Usage: python check_rules.py [out.json]
"""
import json
import random
import sys

TM = "1RB0LC_0RC0RF_0RD0RH_1LE---_0LF1LG_1RD1LA_1RC1LA_0LF0LA"
ST = 'ABCDEFGH'
TT = [[None if ch[i:i + 3] == '---' else (int(ch[i]), 1 if ch[i + 1] == 'R' else -1, ST.index(ch[i + 2]))
       for i in (0, 3)] for ch in TM.split('_')]
D = 3


def run(X, W, W2, maxsteps, first_event=False, allow_x=False):
    """start 0^inf X W 00 D> 0^inf; target 0^inf X W2 00 D> 0^inf.  Returns (steps or None, status)."""
    pad = 64 + 2 * len(W2)
    n = pad + len(X) + max(len(W), len(W2)) + pad
    tape = bytearray(n)
    xb = pad
    for i, v in enumerate(X):
        tape[xb + i] = v
    wb = xb + len(X)
    for i, v in enumerate(W):
        tape[wb + i] = v
    pos, st = wb + len(W) + 2, D
    tpos = wb + len(W2) + 2
    target = bytearray(n)
    target[xb:xb + len(X)] = bytes(X)
    target[wb:wb + len(W2)] = bytes(W2)
    hi = pos
    for s in range(1, maxsteps + 1):
        e = TT[st][tape[pos]]
        if e is None:
            return s - 1, 'HALT'
        tape[pos] = e[0]
        pos += e[1]
        st = e[2]
        if pos < wb and not allow_x:
            return s, 'VISITED_X'
        if pos >= n - 2:
            return s, 'OVERFLOW'
        if pos > hi:
            hi = pos
        if st == D and tape[pos] == 0 and pos >= hi and tape[pos - 1] == 0 and tape[pos - 2] == 0:
            if pos == tpos and tape == target:
                return s, 'OK'
            if first_event:
                return s, 'WRONG_FIRST_EVENT'
    return None, 'TIMEOUT'


def run_blank(W, W2, maxsteps):
    """X = 0^inf: the word may also move left, so the target is aligned at the head (as in the Coq statements):
    0^inf W2 0 0 D> 0^inf with the last cell of W2 three cells left of the head."""
    if W == W2:
        return 0, 'OK'
    pad = 64 + 2 * len(W2) + len(W)
    n = pad + max(len(W), len(W2)) + pad
    tape = bytearray(n)
    wb = pad
    for i, v in enumerate(W):
        tape[wb + i] = v
    pos, st = wb + len(W) + 2, D
    tw = bytes(W2)
    ones_target = sum(W2)
    for s in range(1, maxsteps + 1):
        e = TT[st][tape[pos]]
        if e is None:
            return s - 1, 'HALT'
        tape[pos] = e[0]
        pos += e[1]
        st = e[2]
        if pos <= 1 or pos >= n - 2:
            return s, 'OVERFLOW'
        if st == D and tape[pos] == 0 and tape[pos - 1] == 0 and tape[pos - 2] == 0:
            b = pos - 2 - len(tw)
            if b >= 0 and tape[b:pos - 2] == tw and not any(tape[:b]) and not any(tape[pos:]):
                return s, 'OK'
    return None, 'TIMEOUT'


def ones(n):
    return [1] * n


def Cw(a, k):
    return [1] + [1, 0] * a + [1, 1] + [1, 0] * k + [1]


def Dw(a, i):
    return [1] + [1, 0] * a + ones(6 * i + 3)


def main():
    random.seed(76450)
    ctxs = [[]] + [[random.randint(0, 1) for _ in range(random.randint(1, 10))] for _ in range(12)]
    ctxs += [[1], [1, 0], [0, 1], [1, 1], [1, 0, 1]]
    results = []
    fails = 0

    def rec(rule, params, res):
        nonlocal fails
        steps, status = res
        results.append(dict(rule=rule, params=params, steps=steps, status=status))
        if status != 'OK':
            fails += 1
            print('FAIL', rule, params, status, steps)

    for X in ctxs:
        for m in range(0, 30):
            rec('R1', dict(m=m, X=X), run(X, [0] + ones(3 * m + 1), ones(3 * m + 6), 10 ** 6, first_event=True))
        for i in range(0, 20):
            rec('R0o', dict(i=i, X=X), run(X, [0] + ones(6 * i + 3), [1] + [1, 0] * (3 * i + 2) + [1], 10 ** 6,
                                            first_event=True))
    for i in range(0, 40):
        rec('T1', dict(i=i), run_blank(ones(6 * i + 4), [1] + [1, 0] * (3 * i + 5) + [1], 10 ** 6))
        rec('T2', dict(j=i), run_blank(ones(6 * i + 2), [1] + [1, 0] * (3 * i + 1) + [1, 1, 1, 0, 1, 0, 1], 10 ** 6))
    for a in range(0, 6):
        for k in range(0, 25):
            rec('C_D', dict(a=a, k=k), run_blank(Cw(a, k), Dw(a, k), 10 ** 7))
        for i in range(0, 15):
            rec('Dstep', dict(a=a, i=i), run_blank(Dw(a + 1, i), Dw(a, 3 * i + 2), 10 ** 8))
    for i in range(0, 8):
        rec('Dtop', dict(i=i), run_blank(Dw(0, i), Dw(9 * i + 16, 2), 10 ** 8))
    # documented halting situation (never produced by the family): X ending in 1, then 0 1^(3m+2)
    halts = 0
    for X in ([1], [1, 1], [0, 1], [1, 0, 1]):
        for m in range(0, 10):
            st, status = run(X, [0] + ones(3 * m + 2), ones(3 * m + 7), 10 ** 5, allow_x=True)
            halts += status == 'HALT'
    summary = '%d rule cases, %d failures; halting situation X1 0 1^(3m+2): %d/40 halt' % (len(results), fails, halts)
    print(summary)
    if len(sys.argv) > 1:
        json.dump(dict(summary=summary, results=results), open(sys.argv[1], 'w'), indent=0)


if __name__ == '__main__':
    main()
