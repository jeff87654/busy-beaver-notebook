"""members.py: expand the 110 tier-1 families (hand/tier1_in.tsv) to member machines using collect.py's family key."""
import glob, os, collections
H = os.path.dirname(os.path.abspath(__file__)); NL = os.path.join(H, '..', '..')
fam = collections.defaultdict(list)
for p in sorted(glob.glob(os.path.join(NL, 'full_out', 'p*.tsv'))):
    for l in open(p):
        if l.startswith(('#', 'machine')): continue
        f = l.rstrip('\n').split('\t')
        if len(f) < 18: continue
        def fl(x):
            try: return float(x)
            except ValueError: return 0.0
        if not (fl(f[3]) >= 9.8 or (fl(f[11]) >= 9.8 and f[11] != '99.00')): continue
        fam[(f[3], f[4], f[6], f[9], f[16], f[11])].append(f)
rep = {}
for k, v in fam.items(): rep[v[0][0]] = v
out = open(os.path.join(H, 'members.tsv'), 'w')
n = 0
for i, l in enumerate(open(os.path.join(H, '..', 'tier1_in.tsv'))):
    if i == 0: continue
    f = l.rstrip('\n').split('\t'); m = f[3]
    v = rep.get(m)
    if v is None: print('MISSING', m); continue
    if len(v) != int(f[4]): print('SIZE', m, len(v), f[4])
    for g in v:
        out.write(f'{i}\t{m}\t{g[0]}\t{g[1]}\t{f[5]}\t{f[7]}\n'); n += 1
print('members', n)
