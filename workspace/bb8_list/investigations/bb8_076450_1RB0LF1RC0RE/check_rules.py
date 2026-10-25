"""Exact literal checks of the rules of 1RB0LF_1RC0RE_1LD1LC_1LA0LD_1LB1RA_1RG1LG_0LH0RD_---1RF.
Every start is  0^inf A>0 <word> r 0^inf  with r a random bit word; we run with no acceleration until the next
config with state A reading 0 and blank tape to its left (or until halting), require the exact predicted tape,
and require that no cell of r was ever visited.

  O  (p>=0): A>0 1^(2p+1) 0 r      -> A>0 1^(2p+5) r
  E  (p>=1): A>0 1^(2p) 0 0 1 r    -> A>0 1 0^(2p-1) 1^5 r
  R2 (q>=1): A>0 1^(6q+2) 0 0 0 r  -> A>0 1^8 (001)^(2q-1) 0 0 0 1 r
  R4 (q>=0): A>0 1^(6q+4) 0 0 0 r  -> A>0 1 (001)^(2q+1) 0 0 0 1 r
  R0 (q>=1): A>0 1^(6q) 0 0 0 r    -> halts: H>0 0 1 0 1 (001)^(2q-1) 0 0 0 1 r   (H0 undefined)
"""
import sys, random, json, argparse
from lit import parse, ST

ap = argparse.ArgumentParser()
ap.add_argument('--tm', default="1RB0LF_1RC0RE_1LD1LC_1LA0LD_1LB1RA_1RG1LG_0LH0RD_---1RF")
ap.add_argument('--pmax', type=int, default=120)
ap.add_argument('--tails', type=int, default=3)
ap.add_argument('--out', default=None)
args = ap.parse_args()
T = parse(args.tm)
random.seed(12345)

def run(word, rlen):
    n = len(word)
    pad = 4 * n + 64
    tape = bytearray(pad) + bytearray(int(c) for c in word) + bytearray(pad)
    pos = pad - 1
    rstart = pad + n - rlen          # first cell of r
    st = 0
    steps = 0
    maxpos = pos
    while True:
        s = tape[pos]
        e = T[st][s]
        if e is None:
            kind = 'HALT'; break
        w, d, q = e
        tape[pos] = w; pos += d; st = q; steps += 1
        if pos > maxpos: maxpos = pos
        if pos <= 0 or pos >= len(tape) - 1:
            return ('OUT', steps, None, None, None, None, False)
        if st == 0 and tape[pos] == 0 and not any(tape[:pos]):
            kind = 'A0'; break
        if steps > 10**7:
            return ('LIMIT', steps, None, None, None, None, False)
    hi = len(tape) - 1
    while hi > pos and tape[hi] == 0: hi -= 1
    right = ''.join(map(str, tape[pos + 1:hi + 1]))
    leftblank = not any(tape[:pos])
    return (kind, steps, leftblank, ST[st], tape[pos], right, maxpos < rstart)

def rtail():
    L = random.randint(0, 12)
    return ''.join(random.choice('01') for _ in range(L))

def strip0(w):
    return w.rstrip('0')

RULES = {
    'O':  (range(0, args.pmax), lambda p: ('1' * (2*p+1) + '0', 'A0', '1' * (2*p+5))),
    'E':  (range(1, args.pmax), lambda p: ('1' * (2*p) + '001', 'A0', '1' + '0' * (2*p-1) + '11111')),
    'R2': (range(1, args.pmax // 3), lambda q: ('1' * (6*q+2) + '000', 'A0', '1' * 8 + '001' * (2*q-1) + '0001')),
    'R4': (range(0, args.pmax // 3), lambda q: ('1' * (6*q+4) + '000', 'A0', '1' + '001' * (2*q+1) + '0001')),
    'R0': (range(1, args.pmax // 3), lambda q: ('1' * (6*q) + '000', 'HALT', '0101' + '001' * (2*q-1) + '0001')),
}
res = {}
allok = True
for name, (rng, f) in RULES.items():
    ok = bad = 0
    steps = {}
    for p in rng:
        for t in range(args.tails):
            r = '' if t == 0 else rtail()
            lhs, kind, rhs = f(p)
            kind2, st, leftblank, state, sym, right, untouched = run(lhs + r, len(r))
            want_state = 'A' if kind == 'A0' else 'H'
            good = (kind2 == kind and leftblank and state == want_state and sym == 0 and untouched
                    and strip0(right) == strip0(rhs + r))
            if good:
                ok += 1
                if t == 0: steps[p] = st
            else:
                bad += 1
                print('FAIL', name, p, repr(r), kind2, state, right[:80] if right else right, untouched)
    res[name] = dict(ok=ok, bad=bad, steps=steps)
    allok &= bad == 0
    print('%-3s %5d ok %d fail   steps(first 5): %s' % (name, ok, bad, [steps.get(i) for i in list(rng)[:5]]))
print('ALL OK' if allok else 'FAILURES')
if args.out:
    json.dump(dict(tm=args.tm, results=res), open(args.out, 'w'), indent=1)
