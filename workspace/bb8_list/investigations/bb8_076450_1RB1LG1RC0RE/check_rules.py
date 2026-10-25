"""Exact literal checks of the rules of 1RB1LG_1RC0RE_1LD1LC_1LA0LD_1LB1RF_1RC1LG_---0LH_1RA1LF
(and of any machine given with --tm).  Every start is  0^inf A>0 <word> r 0^inf  with r a random bit word;
we run with no acceleration until the next config with state A reading 0 and blank tape to its left
(or until halting), require the exact predicted tape, and require that no cell of r was ever visited.

  O (p>=0):  A>0 1^(2p+1) 0 r        -> A>0 1^(2p+5) r
  E (p>=1):  A>0 1^(2p) 0 1 1 r      -> A>0 1 0^(2p-1) 1^5 r
  Z4 (q>=0): A>0 1^(6q+4) 0 0 r      -> A>0 1^4 (011)^(2q+1) 0 0 1 r
  Z0 (q>=0): A>0 1^(6q+6) 0 0 r      -> A>0 1 0 0 1^5 (011)^(2q) 0 0 1 r
  Z2 (q>=0): A>0 1^(6q+2) 0 0 r      -> halts: G>0 (110)^(2q+1) 0 1 r   (G0 undefined)
"""
import sys, random, json, argparse
from lit import parse, ST

ap = argparse.ArgumentParser()
ap.add_argument('--tm', default="1RB1LG_1RC0RE_1LD1LC_1LA0LD_1LB1RF_1RC1LG_---0LH_1RA1LF")
ap.add_argument('--pmax', type=int, default=120)
ap.add_argument('--tails', type=int, default=3)
ap.add_argument('--out', default=None)
args = ap.parse_args()
T = parse(args.tm)
random.seed(12345)

def run(word, rlen):
    """word = full right side (incl. r at the end, r = last rlen cells). Returns (kind, steps, leftside, state, rightword, maxpos_ok)."""
    n = len(word)
    pad = 4 * n + 64
    tape = bytearray(pad) + bytearray(int(c) for c in word) + bytearray(pad)
    pos = pad - 1
    rstart = pad + n - rlen          # first cell of r
    lo = pos
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
        if pos < lo: lo = pos
        if pos <= 0 or pos >= len(tape) - 1:
            return ('OUT', steps, None, None, None, False)
        if st == 0 and tape[pos] == 0 and not any(tape[:pos]):
            kind = 'A0'; break
        if steps > 10**7:
            return ('LIMIT', steps, None, None, None, False)
    hi = len(tape) - 1
    while hi > pos and tape[hi] == 0: hi -= 1
    right = ''.join(map(str, tape[pos + 1:hi + 1]))
    leftblank = not any(tape[:pos])
    return (kind, steps, leftblank, ST[st], right, maxpos < rstart)

def rtail():
    L = random.randint(0, 12)
    return ''.join(random.choice('01') for _ in range(L))

def strip0(w):
    return w.rstrip('0')

RULES = {
    'O':  (range(0, args.pmax), lambda p: ('1' * (2*p+1) + '0', 'A0', '1' * (2*p+5))),
    'E':  (range(1, args.pmax), lambda p: ('1' * (2*p) + '011', 'A0', '1' + '0' * (2*p-1) + '11111')),
    'Z4': (range(0, args.pmax // 3), lambda q: ('1' * (6*q+4) + '00', 'A0', '1111' + '011' * (2*q+1) + '001')),
    'Z0': (range(0, args.pmax // 3), lambda q: ('1' * (6*q+6) + '00', 'A0', '100' + '11111' + '011' * (2*q) + '001')),
    'Z2': (range(0, args.pmax // 3), lambda q: ('1' * (6*q+2) + '00', 'HALT', '110' * (2*q+1) + '01')),
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
            kind2, st, leftblank, state, right, untouched = run(lhs + r, len(r))
            want_state = 'A' if kind == 'A0' else 'G'
            good = (kind2 == kind and leftblank and state == want_state and untouched
                    and strip0(right) == strip0(rhs + r) and (kind == 'HALT' or True))
            if kind == 'HALT':
                # halting config must be G reading 0 with blank to the left
                good = good and state == 'G'
            if good:
                ok += 1
                if t == 0: steps[p] = st
            else:
                bad += 1
                print('FAIL', name, p, repr(r), kind2, state, right[:80], untouched)
    res[name] = dict(ok=ok, bad=bad, steps=steps)
    allok &= bad == 0
    print('%-3s %5d ok %d fail   steps(p=0..4): %s' % (name, ok, bad, [steps.get(i) for i in list(rng)[:5]]))
print('ALL OK' if allok else 'FAILURES')
if args.out:
    json.dump(dict(tm=args.tm, results=res), open(args.out, 'w'), indent=1)
