"""scalechk.py FILE.tsv.. : for each distinct leaf machine with a phase-1 restart (MAX2/RESTART*/HALT2), first restart
counter under (std k=17 n=41), (std k=17 n=329), (std k=29 n=41), (big k=17 n=41).  Accumulator-sized iff big gives
~4*2539+3+delta (>= 10000)."""
import sys, threading
from t1lib import run, start_word, far_of, rsig
def first(M, k, n, pol):
    R0 = 2539 if pol == 'big' else 19; rs = []
    def cb(st, kind, d):
        if kind == 'K':
            s = rsig(d[0][:-2])
            if s and not d[1] and s[1] >= 40 and st > 0: rs.append((s[1], len(s[0]), st)); return 1
    kind, st, d, v = run(M, start_word([0] + [1] * n + [1, R0], far_of(k)), 30, cb=cb, policy=pol, maxs=4 * 10**9)
    return f'c={rs[0][0]},P{rs[0][1]}@{rs[0][2]}' if rs else (f'H{d[0]}{d[1]}' if kind == 'H' else kind)
import os
CASES = [tuple(int(x) if i < 2 else x for i, x in enumerate(c.split(':'))) for c in os.environ.get('CASES', '17:41:std,17:329:std,29:41:std,17:41:big').split(',')]
def go():
    seen = set()
    for fn in sys.argv[1:]:
        for line in open(fn):
            f = line.rstrip('\n').split('\t')
            if len(f) < 5 or 'R1:' not in f[4] or f[1] in ('KFAIL',) or f[0] in seen: continue
            if 'R1:c=79,d=0' in f[4] and 'R2:c=79' in f[4]: continue
            seen.add(f[0])
            res = [first(f[0], k, n, p) for k, n, p in CASES]
            print(f'{fn}\t{f[1]}\t' + '\t'.join(res) + '\t' + '_'.join(f[0].split('_')[9:]), flush=True)
threading.stack_size(200 * 1024 * 1024); sys.setrecursionlimit(400000)
t = threading.Thread(target=go); t.start(); t.join()
