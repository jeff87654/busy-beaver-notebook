"""Exact literal checks of the rules of 1RB1LF_1RC1RE_1RD0LG_0RE1LD_1LA0LC_0RG1LA_---0LH_1RA1LC.

Every start is  0^inf A>0 <word> r 0^inf  with r a random bit word (or r = 0^inf where the rule needs it);
we run with no acceleration until the next config with state A reading 0 and blank tape to its left
(or a halt), require the exact predicted tape, and require that no cell of r was ever visited.

Cell-level rules (the Coq phase lemmas are the instances marked *):
  P (p>=2):  A>0 1^(2p) 0 0 r       -> A>0 1^(2p+5) r                 (* P6: 2p = 6i+6)
             (p = 1 gives the same tape but reads the first cell of r, so it is excluded)
  R (p>=1):  A>0 1^(2p+1) 0 0 r     -> A>0 1^5 0 1^(2p+3) r           (* R6: 2p+1 = 6j+5, r = 0^inf)
  C (j>=0):  A>0 1^(6j+5) 0 1 r     -> A>0 1^6 (001)^(2j+1) 0 0 0 r   (* C6)
Family rules (W j m = 0^inf A>0 1^(6j+5) 0 1^m 0^inf), run to the first later W configuration:
  Wstep  (j, m >= 0): W(j, m+1) -> W(2j+2, m)
  Wreset (j >= 0):    W(j, 0)   -> W(0, 6j+7)
Also records the exact step counts (for fit_steps.py).
"""
import sys, random, json, argparse, re
from lit import parse, ST

ap = argparse.ArgumentParser()
ap.add_argument('--tm', default="1RB1LF_1RC1RE_1RD0LG_0RE1LD_1LA0LC_0RG1LA_---0LH_1RA1LC")
ap.add_argument('--pmax', type=int, default=150)
ap.add_argument('--jmax', type=int, default=50)
ap.add_argument('--wj', type=int, default=40)
ap.add_argument('--wm', type=int, default=6)
ap.add_argument('--tails', type=int, default=3)
ap.add_argument('--out', default=None)
args = ap.parse_args()
T = parse(args.tm)
random.seed(20260927)


def run(word, rlen, want=None, maxsteps=10**8):
    """word = full right side (r = last rlen cells). Runs to the next left-edge A0 config (or to the first one
    whose right word matches regex `want`). Returns (kind, steps, rightword, r_untouched)."""
    n = len(word)
    pad = 4 * n + 256
    tape = bytearray(pad) + bytearray(int(c) for c in word) + bytearray(pad)
    pos = pad - 1
    rstart = pad + n - rlen
    st = 0
    steps = 0
    maxpos = pos
    lo = pos
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
        if st == 0 and tape[pos] == 0 and not any(tape[lo:pos]):
            hi = len(tape) - 1
            while hi > pos and tape[hi] == 0: hi -= 1
            right = ''.join(map(str, tape[pos + 1:hi + 1]))
            if want is None or want(right):
                return ('A0', steps, right, maxpos < rstart)
        if steps > maxsteps:
            return ('LIMIT', steps, None, False)


def rtail():
    L = random.randint(0, 12)
    return ''.join(random.choice('01') for _ in range(L))


RULES = {
    'P': (range(2, args.pmax), True, lambda p: ('1' * (2*p) + '00', '1' * (2*p+5))),
    'R': (range(1, args.pmax), True, lambda p: ('1' * (2*p+1) + '00', '11111' + '0' + '1' * (2*p+3))),
    'C': (range(0, args.jmax), True, lambda j: ('1' * (6*j+5) + '01', '111111' + '001' * (2*j+1) + '000')),
}
def WPAT(w):
    """is w the word of some W j m, i.e. 1^(6j+5) 0 1^m (m >= 0)?"""
    mt = re.fullmatch(r'(1+)(01*)?', w)
    return bool(mt) and len(mt.group(1)) % 6 == 5


def W(j, m):
    return '1' * (6*j+5) + ('0' + '1' * m if m else '')


res = {}
allok = True
for name, (rng, tails, f) in RULES.items():
    ok = bad = 0
    steps = {}
    for p in rng:
        for t in range(args.tails if tails else 1):
            r = '' if t == 0 else rtail()
            lhs, rhs = f(p)
            kind, st, right, untouched = run(lhs + r, len(r))
            good = kind == 'A0' and untouched and right.rstrip('0') == (rhs + r).rstrip('0')
            if good:
                ok += 1
                if t == 0: steps[p] = st
            else:
                bad += 1
                print('FAIL', name, p, repr(r), kind, (right or '')[:80], untouched)
    res[name] = dict(ok=ok, bad=bad, steps=steps)
    allok &= bad == 0
    print('%-6s %5d ok %d fail   steps(first 5): %s' % (name, ok, bad, [steps.get(i) for i in list(rng)[:5]]))

# family rules
for name in ('Wstep', 'Wreset'):
    ok = bad = 0
    steps = {}
    for j in range(args.wj):
        for m in (range(0, args.wm) if name == 'Wstep' else [None]):
            if name == 'Wstep':
                start, pred = W(j, m + 1), W(2*j+2, m)
                key = '%d,%d' % (j, m)
            else:
                start, pred = W(j, 0), W(0, 6*j+7)
                key = '%d' % j
            kind, st, right, _ = run(start, 0, want=WPAT)
            if kind == 'A0' and right == pred:
                ok += 1; steps[key] = st
            else:
                bad += 1
                print('FAIL', name, key, kind, (right or '')[:80])
    res[name] = dict(ok=ok, bad=bad, steps=steps)
    allok &= bad == 0
    print('%-6s %5d ok %d fail' % (name, ok, bad))
print('ALL OK' if allok else 'FAILURES')
if args.out:
    json.dump(dict(tm=args.tm, results=res), open(args.out, 'w'), indent=1)
