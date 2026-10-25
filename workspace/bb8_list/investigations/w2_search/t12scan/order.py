"""order.py M SW B [--n 329 --k 17 --maxs 5e11]: size-order test.  Big policy (restart counter trimmed to its class
mod 42), jump representatives U = 19 + 2520 for stages < SW and U = 19 + 2520*B from stage SW on, so that at the
round-2 end the accumulator (~U_B) is far larger than the depth list (built from U_1 increments): emulates the true
order k1 << depth << accumulator that the fixed-U follower violates."""
import sys, threading, argparse
from ilib import stage, rsig, far_of, word_of, SUF, rle
ap = argparse.ArgumentParser(); ap.add_argument('M'); ap.add_argument('sw', type=int); ap.add_argument('B', type=int)
ap.add_argument('--n', type=int, default=329); ap.add_argument('--k', type=int, default=17); ap.add_argument('--maxs', type=float, default=5e11)
ap.add_argument('--S', type=int, default=40)
a = ap.parse_args()
def go():
    word = far_of(a.k) + word_of([0] + [1] * a.n + [1, 19]) + SUF
    for st in range(a.S):
        bk = a.B if st >= a.sw else 1
        kind, d = stage(a.M, word, int(a.maxs), 'big', bigk=bk, ctrim=41)
        if kind != 'K': print(f'{st} {kind} {d.get("slot","")}  (bigk {bk})', flush=True); return
        t = d['toks']; print(st, 'bigk', bk, rle(t[:-2])[:140], '| a,r', t[-2:], 'far', len(d['far']), flush=True)
        word = d['newword']
    print('MAX')
threading.stack_size(250 * 1024 * 1024); sys.setrecursionlimit(300000)
t = threading.Thread(target=go); t.start(); t.join()
