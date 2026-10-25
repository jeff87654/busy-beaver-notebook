"""nextsym.py MACHINE K WORD1:STATE:STEPS WORD2:STATE:STEPS ... : for each transition (q,s), the set of k-symbol
sequences read after it (along the path), per run; prints transitions whose sequence set in the LAST run contains
sequences never seen in the other runs."""
import sys, collections
from prof import parse
m, K = sys.argv[1], int(sys.argv[2])
t = parse(m)
runs = []
for spec in sys.argv[3:]:
    wf, q0, N = spec.split(':'); N = int(N)
    w = open(wf).read().strip() if wf != '-' else ''
    off = 3_000_000; tape = bytearray(off) + bytearray(int(c) for c in w) + bytearray(6_000_000)
    pos = off + len(w); q = ord(q0) - 65
    hist = []
    seqs = collections.defaultdict(collections.Counter)
    for st in range(N):
        c = tape[pos]
        hist.append((q, c))
        if (q, c) not in t: break
        wr, d, nq = t[(q, c)]; tape[pos] = wr; pos += d; q = nq
    for i in range(len(hist) - K):
        key = chr(65+hist[i][0]) + str(hist[i][1])
        seqs[key][''.join(str(hist[i+j][1]) for j in range(1, K+1))] += 1
    runs.append(seqs)
last = runs[-1]
for key in sorted(last):
    other = set()
    for r in runs[:-1]: other |= set(r[key])
    new = {s: n for s, n in last[key].items() if s not in other}
    if new: print(key, 'E1-only next-symbol sequences:', dict(sorted(new.items(), key=lambda x: -x[1])[:6]), 'others:', sorted(other)[:8])
