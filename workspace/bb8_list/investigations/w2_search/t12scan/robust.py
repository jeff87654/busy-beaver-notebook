"""robust.py IN OUT: for each machine (first column) print the RSIG (stage, |P|, c) sequences at (k, n) in
(17,329) (17,371) (17,2849) (29,329) (41,371), std; ROBUST if the first two RSIGs' (|P| up to k, c) agree."""
import sys, threading
from ilib import stage, rsig, far_of, word_of, SUF
def rs(M, k, n, S=160):
    word = far_of(k) + word_of([0] + [1] * n + [1, 19]) + SUF; out = []
    for st in range(S):
        kind, d = stage(M, word, 10**9)
        if kind != 'K': return out, f'{kind}{d.get("slot","")}@{st}'
        r = rsig(d['toks'])
        if r and st > 0 and (not out or st - out[-1][0] > 3): out.append((st, len(r[0]), r[1]))
        if len(out) >= 3: return out, 'RS3'
        word = d['newword']
    return out, 'MAX'
def go():
    fo = open(sys.argv[2], 'w')
    for line in open(sys.argv[1]):
        f = line.rstrip('\n').split('\t')
        if len(f) < 4 or f[2] != 'ok' or '2: 0, 3: 0' in f[3]: continue
        M = f[0]; res = []
        for k, n in ((17, 329), (17, 371), (17, 2849), (29, 329), (41, 371)):
            o, e = rs(M, k, n); res.append((k, n, o, e))
        sig = [tuple(c for _, _, c in o[:2]) for _, _, o, _ in res]
        ok = all(s == sig[0] and len(s) == 2 for s in sig)
        row = f'{M}\t{"ROBUST" if ok else "fragile"}\t{f[3]}\t{f[4] if len(f) > 4 else ""}\t' + ' | '.join(f'k{k}n{n}:{e}:' + ','.join(f'{s}/{p}/{c}' for s, p, c in o) for k, n, o, e in res)
        print(row[:400], flush=True); fo.write(row + '\n'); fo.flush()
threading.stack_size(250 * 1024 * 1024); sys.setrecursionlimit(300000)
t = threading.Thread(target=go); t.start(); t.join()
