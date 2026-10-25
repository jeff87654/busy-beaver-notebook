"""realbig.py M [--q1 3 --q2 0]: follow M from the real start (b0 = 6) under the BIG policy with a two-phase counter
trim: the round-1 counter (first R-sized '2 5 1^m') is trimmed to m mod 42 + 42*q1 (keeps the round-1 far run k large
and in class), every later R-sized counter to m mod 42 + 42*q2 (short round 2).  Prints RSIGs and the outcome."""
import sys, threading, argparse
import ilib
from ilib import stage, rsig, real_start, rle
ap = argparse.ArgumentParser(); ap.add_argument('M'); ap.add_argument('--q1', type=int, default=3); ap.add_argument('--q2', type=int, default=0)
ap.add_argument('--S', type=int, default=200); ap.add_argument('--v', action='store_true'); ap.add_argument('--maxs', type=float, default=3e9)
a = ap.parse_args()
seen = [0]
def trim(new, ct):
    out = list(new); i = 0
    while i + 2 < len(out) - 2:
        if out[i] == 2 and out[i + 1] == 5:
            j = i + 2
            while j < len(out) - 2 and out[j] == 1: j += 1
            m = j - i - 2
            if m > 1000:
                q = a.q1 if seen[0] == 0 else a.q2
                seen[0] += 1
                m2 = (m % 42) + 42 * q
                out = out[:i + 2] + [1] * m2 + out[j:]; j = i + 2 + m2
            i = j
        else:
            i += 1
    return out
ilib.trim_counter = trim
def go():
    word, head, state = real_start(6); rs = []
    for st in range(a.S):
        kind, d = stage(a.M, word, int(a.maxs), 'big', ctrim=1, head=head, state=state); head, state = None, 'G'
        if kind != 'K': print(f'{kind} {d.get("slot","")} at stage {st}; RS=', rs, flush=True); return
        r = rsig(d['toks'])
        if r and st > 0 and (not rs or st - rs[-1][0] > 3): rs.append((st, len(r[0]), r[1], r[2]))
        if a.v: print(st, rle(d['toks'][:-2])[:160], 'far', len(d['far']), flush=True)
        word = d['newword']
    print('MAX RS=', rs)
threading.stack_size(250 * 1024 * 1024); sys.setrecursionlimit(300000)
t = threading.Thread(target=go); t.start(); t.join()
