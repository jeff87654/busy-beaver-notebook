"""kcheck.py FILE.tsv [ks]: for each leaf with a phase-1 restart (R1:), rerun the eater (slots as in the leaf) from
far_k + [0 1^41|1|19] for k in ks (default 17,77,137) and report the restart counter per k (k-periodicity filter)."""
import sys, threading
from t1lib import run, start_word, far_of, rsig
ks = [int(x) for x in (sys.argv[2] if len(sys.argv) > 2 else '17,77,137').split(',')]
def eat(M, k):
    rs = []
    def cb(st, kind, d):
        if kind == 'K':
            s = rsig(d[0][:-2])
            if s and not d[1] and s[1] >= 40: rs.append(s[1]); return 1
    kind, st, d, v = run(M, start_word([0] + [1] * 41 + [1, 19], far_of(k)), 40, cb=cb, maxs=10**9)
    return f'c={rs[0]}' if rs else (f'H{d[0]}{d[1]}' if kind == 'H' else kind)
def go():
    seen = set()
    for line in open(sys.argv[1]):
        f = line.rstrip('\n').split('\t')
        if 'R1:' not in line or f[0] in seen: continue
        seen.add(f[0])
        res = [eat(f[0], k) for k in ks]
        ok = len(set(res)) == 1
        print(('PERIODIC ' if ok else 'kfail    ') + ' '.join(f'k{k}:{r}' for k, r in zip(ks, res)) + '\t' + f[0] + '\t' + f[1], flush=True)
threading.stack_size(64 * 1024 * 1024); sys.setrecursionlimit(30000)
t = threading.Thread(target=go); t.start(); t.join()
