import sys, re, collections
recs = {}; cur = None
for f in sys.argv[1:]:
    for l in open(f):
        if l.startswith('###'):
            p = l.split(); cur = p[1][56:]; recs[cur] = {'res': p[3], 'n': p[4], 'K': []}
        elif ' K: ' in l:
            k = l.split(' K: ', 1)[1].strip()
            k = re.sub(r' far=.*', ' far', k)
            recs[cur]['K'].append(k)
        elif ' HALT ' in l or l.split()[1:2] == ['T']:
            recs[cur]['end'] = l.strip()[:80]
g = collections.defaultdict(list)
for m, d in recs.items():
    sig = (d['res'], tuple(d['K'][-6:]))
    g[sig].append(m)
for i, (sig, ms) in enumerate(sorted(g.items(), key=lambda x: -len(x[1]))):
    d = recs[ms[0]]
    print(f'G{i} n={len(ms)} {sig[0]} {d["n"]} K0={d["K"][0][:60] if d["K"] else "-"} last={d["K"][-1][:90] if d["K"] else "-"}')
    print('    ', ' '.join(ms))
