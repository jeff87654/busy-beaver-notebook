"""Analyse bprobe output: per machine, events whose output token count depends on r (list-length growth with the
accumulator = the level-2 mechanism), halting events, unresolved events.  python bpana.py BP.tsv"""
import sys, collections
rows = collections.defaultdict(lambda: collections.defaultdict(dict))
for l in open(sys.argv[1]):
    f = l.rstrip('\n').split('\t')
    m, Z, k, r, kind, steps, n = f[0], int(f[4]), int(f[5]), int(f[6]), f[7], int(f[8]), int(f[9])
    rows[m][(Z, k)][r] = (kind, n, f[10] if len(f) > 10 else '')
grow = collections.defaultdict(list); summ = {}
for m, ev in rows.items():
    cnt = collections.Counter()
    for (Z, k), byr in ev.items():
        kinds = ''.join(byr[r][0] for r in sorted(byr))
        cnt[(Z, kinds[0] if len(set(kinds)) == 1 else 'mix')] += 1
        ns = [byr[r][1] for r in sorted(byr) if byr[r][0] == 'J']
        if len(ns) >= 3 and len(set(ns)) > 1:
            grow[m].append((Z, k, [(r, byr[r][0], byr[r][1]) for r in sorted(byr)]))
    summ[m] = cnt
print('machines', len(rows))
print('machines with r-dependent output length:', len(grow))
for m, g in sorted(grow.items(), key=lambda x: -len(x[1])):
    print(m[61:], m[56:60], len(g), g[:4])
agg = collections.Counter()
for m, c in summ.items():
    agg[tuple(sorted((f'Z{z}{kd}', v) for (z, kd), v in c.items()))] += 1
print('distinct event-kind profiles', len(agg))
