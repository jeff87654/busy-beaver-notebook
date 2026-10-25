"""rhist.py: second-pass statistics from rpil/: gate pass counts and the first-reset-time histogram of the passers."""
import glob, collections
n = g = gf = 0; h = collections.Counter(); hf = collections.Counter(); nores = 0
for f in sorted(glob.glob('rpil/r*.tsv')):
    for l in open(f):
        x = l.rstrip('\n').split('\t')
        if len(x) < 11 or x[0] == 'machine': continue
        n += 1; p2 = float(x[3]); nsr = int(x[9]); sr0 = float(x[10])
        if not (p2 >= 8.0 or nsr >= 2): continue
        g += 1
        if sr0 < 0: nores += 1; b = 'none'
        else: b = int(sr0)
        h[b] += 1
        if p2 >= 8.0: gf += 1; hf[b] += 1
print(f'stage A machines {n}, gate passers {g} ({100*g/max(n,1):.1f}%), of which P2>=8 {gf}; passers without a slot reset {nores}')
print('first slot reset, log10 base steps: bin  all-passers  P2>=8-passers')
for b in sorted(h, key=lambda v: (isinstance(v, str), v)): print(f'  {b!s:>5}  {h[b]:9d}  {hf[b]:9d}')
