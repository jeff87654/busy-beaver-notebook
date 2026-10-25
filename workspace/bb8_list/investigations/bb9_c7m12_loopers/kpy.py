"""kpy.py MACHINE Q MAXSTEPS [--rev] [--word W] [--state S] [--all] [--maxp N]: python K-moment printer: state Q reading 0
on the rightmost visited cell; prints the D-token view of the tape left of the head (--rev: of the reversed tape, i.e.
tokens nearest-first), only when the shape (numbers -> #) changes unless --all.  Start: blank (state A) or word W with
the head on the blank right of it in state S."""
import sys, re, argparse
from tm import parse, dtoks
ap = argparse.ArgumentParser()
ap.add_argument('M'); ap.add_argument('Q'); ap.add_argument('maxs', type=float)
ap.add_argument('--rev', action='store_true'); ap.add_argument('--word', default=''); ap.add_argument('--state', default='A')
ap.add_argument('--all', action='store_true'); ap.add_argument('--maxp', type=int, default=10**9)
a = ap.parse_args()
Q = ord(a.Q) - 65; maxs = int(a.maxs)
T, n = parse(a.M)
N = 1 << 23
tape = bytearray(N); off = N // 2
for i, ch in enumerate(a.word):
    tape[off + i] = ch == '1'
lo = off; pos = off + len(a.word); hi = max(pos, off); q = ord(a.state) - 65
last = None; sim = 0; lastline = ''; prints = 0
step = 0
for step in range(maxs):
    c = tape[pos]
    if q == Q and c == 0 and pos >= hi:
        w = ''.join('1' if x else '0' for x in tape[lo:pos])
        v = dtoks(w[::-1]) if a.rev else dtoks(w)
        sh = re.sub(r'\d+', '#', v)
        if a.all or sh != last:
            if sim: print(f'   ... {sim} similar; last {lastline}')
            print(f'S {step} | {v[:400]}', flush=True); last = sh; sim = 0; prints += 1
            if prints >= a.maxp: break
        else:
            sim += 1; lastline = f'{step} | {v[:400]}'
    t = T.get((q, c))
    if t is None:
        w = ''.join('1' if x else '0' for x in tape[lo:hi + 1])
        print('HALT', step, chr(65 + q), c, 'ones', w.count('1'), '|', dtoks(w)[:300]); sys.exit(0)
    w_, d, nq = t
    tape[pos] = w_; pos += d; q = nq
    if pos < lo: lo = pos
    if pos > hi: hi = pos
if sim: print(f'   ... {sim} similar; last {lastline}')
print('END', step + 1)
