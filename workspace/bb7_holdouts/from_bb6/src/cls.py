"""cls.py OUT.tsv WORLDS... : classify ext.exe outcomes per machine.
per run: IMM (halt, <=2 steps) | SOON (halt, R=1) | REHALT (halt after >=2 exhaustions R) | LOOP1 (run, R=1) | LOOPR (run, R>=2) | OOB
machine class = the multiset over worlds; summary line: machine, counts, max ones ratio vs the world's base score."""
import sys, collections
wones = {}
for fn in sys.argv[2:]:
    for l in open(fn):
        f = l.split()
        if len(f) >= 5: wones[f[1]] = (f[2].count('1') + 1, len(f[2]))
res = collections.defaultdict(list)
for l in open(sys.argv[1]):
    f = l.rstrip('\n').split('\t')
    m, w, st, t, R, G, ones = f[0], f[1], f[2], int(f[3]), int(f[4]), int(f[5]), int(f[6])
    b1, L = wones.get(w, (1, 1)); rs = [int(x) for x in f[9].split(',') if x]
    ep = 1 + sum(1 for i in range(1, len(rs)) if rs[i] - rs[i-1] > 4 * L)   # exhaustion episodes (gap > 4 x world length)
    if R > len(rs): ep += 1 if t - rs[-1] > 4 * L else 0
    if st.startswith('HALT'): c = 'IMM' if t <= 2 else ('SOON' if ep <= 1 else 'REHALT')
    elif st == 'OOB': c = 'OOB'
    else: c = 'LOOP1' if ep <= 1 else 'LOOPR'
    res[m].append((c, w, t, ep, G, ones, ones / b1))
for m, L in res.items():
    cnt = collections.Counter(x[0] for x in L)
    hal = [x for x in L if x[0] in ('SOON', 'REHALT')]
    mr = max((x[6] for x in hal), default=0); mR = max((x[3] for x in L), default=0); mt = max((x[2] for x in hal), default=0)
    key = ','.join(f"{k}:{cnt[k]}" for k in ('IMM', 'SOON', 'REHALT', 'LOOP1', 'LOOPR', 'OOB') if cnt[k])
    print(f"{m}	{key}	maxEp={mR}	maxHaltRatio={mr:.2f}	maxHaltSteps={mt}")
