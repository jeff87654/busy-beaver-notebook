"""ana9.py FILES: 9-state E-only-root leaves (engine intact by construction: H, I are entered only at exhaustions).
Chain analysis as ana2 (family Phi); also flags leaves whose E-map has non-K outcomes (T/X) on the base's rebuild parity."""
import sys, os, collections
from bcfg import BASES
from ana2 import chain, AS
P0 = {'u': 0, 't': 0, 'b': 1, 'c': 1, 'j': 1}
stat = collections.Counter(); cand = []; nonk = []
for fn in sys.argv[1:]:
    tag = os.path.basename(fn).split('_')[1]; fam = BASES[tag][3]
    for l in open(fn):
        f = l.rstrip('\n').split('\t')
        if l.startswith('#') or len(f) < 3: continue
        st = f[2][0]
        if st != 'T': stat['blank ' + st] += 1; continue
        tr, res = chain(fam, f[3:])
        mx = max((r[0] for r in res.values() if r[0] is not None), default=None)
        cyc = any(r[1] for r in res.values())
        r0 = res[P0[tag]]
        stat[f'maxR={mx} cyc={cyc} fromReal={r0[0]}'] += 1
        if (mx is not None and mx >= 1) or cyc: cand.append((tag, f[0], f[1], mx, cyc, r0[0]))
        p = P0[tag]; outs = [c for A, c in zip(AS, f[3:]) if A % 2 == p]
        if any(not c.startswith(('K', 'H')) for c in outs): nonk.append((tag, f[0], f[1], ' '.join(c[:12] for c in f[3:])))
for k, v in sorted(stat.items(), key=lambda x: -x[1]): print(f'{v:8d} {k}')
print('--- chains >= 1 rebuild or class cycles:', len(cand))
for x in cand[:60]: print(*x, sep='\t')
print('--- non-K outcomes on the real rebuild parity:', len(nonk))
for x in nonk[:60]: print(*x, sep='\t')
