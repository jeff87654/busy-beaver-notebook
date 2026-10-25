import json,glob,math,collections
by=collections.defaultdict(list)
for f in sorted(glob.glob('r_*.json')):
    try: d=json.loads(open(f).read().strip())
    except Exception as e: print(f,'BAD',e); continue
    by[d['states']].append(d)
for n in sorted(by):
    runs=by[n]; P=sum(r['probes'] for r in runs)
    print(f"n={n}: {len(runs)} runs, {P} probes")
    for k in ['nodes','holdouts','halters','cpu_seconds']:
        S=sum(r[k]['sum'] for r in runs); Q=sum(r[k]['sumsq'] for r in runs); M=max(r[k]['max'] for r in runs)
        mean=S/P; var=max(Q/P-mean*mean,0); se=math.sqrt(var/P)
        per=[r[k]['sum']/r['probes'] for r in runs]
        print(f"  {k:12s} est={mean:.3e}  se={se:.2e} ({se/mean*100 if mean else 0:.0f}%)  max_single={M:.2e} ({M/S*100 if S else 0:.1f}% of sum)  per-run=[{', '.join(f'{x:.2e}' for x in per)}]")
