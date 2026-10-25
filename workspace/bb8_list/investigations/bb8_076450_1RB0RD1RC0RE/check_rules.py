"""Exact literal checks of the rules of 1RB0RD_1RC0RE_1LD1LC_1LA0LD_1LB1RF_---1LG_0RB1RH_0LB1RG
(or of the machine given with --tm).  Every start is  0^inf A>0 <word> r 0^inf ; r is a random bit word
(or empty when the rule needs the blank tape on the right, marked [blank]).  We run with no acceleration
until the k-th configuration with state A reading 0 and blank tape to its left (k = 1 unless noted), or
until halting, and require the exact predicted tape and (for random r) that no cell of r was visited.

  O1 (n even >= 4): A>0 1^n 0 r              -> A>0 1 0 1^(n+1) r
  L               : A>0 1 0 r                -> A>0 1^5 r
  O  (n even >= 4): A>0 1^n 0 r              -> A>0 1^(n+6) r            (O1 then L; k = 2)
  R  (n odd >= 5) : A>0 1^n 0 0 0 r          -> A>0 1^6 0^(n-1) 1 r
  Z  (m odd >= 3) : A>0 1^m 0 0 1 [blank]    -> A>0 1 0^m 1 1 1 [blank]
  W  (m odd >= 3) : A>0 1^m 0 1 1 1 [blank]  -> A>0 1 0^m 1 1 1 1 0 0 1 [blank]
Also reported (not used): what O does for n = 2 (halts: F reads 0).
"""
import sys, random, json, argparse
from lit import parse, ST

ap = argparse.ArgumentParser()
ap.add_argument('--tm', default="1RB0RD_1RC0RE_1LD1LC_1LA0LD_1LB1RF_---1LG_0RB1RH_0LB1RG")
ap.add_argument('--nmax', type=int, default=240)
ap.add_argument('--tails', type=int, default=3)
ap.add_argument('--out', default=None)
args = ap.parse_args()
T = parse(args.tm)
random.seed(12345)

def run(word, rlen, k=1):
    n = len(word)
    pad = 4 * n + 64
    tape = bytearray(pad) + bytearray(int(c) for c in word) + bytearray(pad)
    pos = pad - 1
    rstart = pad + n - rlen
    st = 0; steps = 0; maxpos = pos; hits = 0
    while True:
        e = T[st][tape[pos]]
        if e is None:
            kind = 'HALT'; break
        w, d, q = e
        tape[pos] = w; pos += d; st = q; steps += 1
        if pos > maxpos: maxpos = pos
        if pos <= 0 or pos >= len(tape) - 1:
            return ('OUT', steps, None, None, None, False)
        if st == 0 and tape[pos] == 0 and not any(tape[:pos]):
            hits += 1
            if hits == k:
                kind = 'A0'; break
        if steps > 10**7:
            return ('LIMIT', steps, None, None, None, False)
    hi = len(tape) - 1
    while hi > pos and tape[hi] == 0: hi -= 1
    right = ''.join(map(str, tape[pos + 1:hi + 1]))
    return (kind, steps, not any(tape[:pos]), ST[st], right, maxpos < rstart)

def rtail():
    L = random.randint(0, 12)
    return ''.join(random.choice('01') for _ in range(L))

N = args.nmax
# name: (parameter range, f(p) -> (lhs, rhs, k), blank_right_only)
RULES = {
    'O1': (range(4, N, 2), lambda n: ('1' * n + '0', '10' + '1' * (n + 1), 1), False),
    'L':  (range(0, 1),    lambda _: ('10', '11111', 1), False),
    'O':  (range(4, N, 2), lambda n: ('1' * n + '0', '1' * (n + 6), 2), False),
    'R':  (range(5, N, 2), lambda n: ('1' * n + '000', '111111' + '0' * (n - 1) + '1', 1), False),
    'Z':  (range(3, N, 2), lambda m: ('1' * m + '001', '1' + '0' * m + '111', 1), True),
    'W':  (range(3, N, 2), lambda m: ('1' * m + '0111', '1' + '0' * m + '1111001', 1), True),
}
res = {}; allok = True
for name, (rng, f, blank_only) in RULES.items():
    ok = bad = 0; steps = {}
    for p in rng:
        for t in range(1 if blank_only else args.tails):
            r = '' if t == 0 else rtail()
            lhs, rhs, k = f(p)
            kind, st, leftblank, state, right, untouched = run(lhs + r, len(r), k)
            good = (kind == 'A0' and leftblank and state == 'A' and (untouched or not r)
                    and right.rstrip('0') == (rhs + r).rstrip('0'))
            if good:
                ok += 1
                if t == 0: steps[p] = st
            else:
                bad += 1
                print('FAIL', name, p, repr(r), kind, state, (right or '')[:80], untouched)
    res[name] = dict(ok=ok, bad=bad, steps=steps)
    allok &= bad == 0
    ks = list(rng)[:4]
    print('%-3s %5d ok %d fail   steps at %s: %s' % (name, ok, bad, ks, [steps.get(i) for i in ks]))
kind, st, *_ = run('110', 0, 1)
print('n=2 in O: A>0 1 1 0 ->', kind, 'after', st, 'steps')
print('ALL OK' if allok else 'FAILURES')
if args.out:
    json.dump(dict(tm=args.tm, results=res), open(args.out, 'w'), indent=1)
