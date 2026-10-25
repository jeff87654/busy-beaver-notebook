"""collect.py: gather the dlscan3 c7m12 rows of interest (LOOPER, MULTI, MULTI?, W1-*, and NOBOUNDARY/REBUILD rows whose
exhaustion chains show a rebuild R) into rows.tsv: machine, grade, undefined slots, chains."""
import glob, re, sys
from pathlib import Path
SRC = r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/nested_detector/scans/c7m12'
SL = ['A0','A1','B0','B1','C0','C1','D0','D1','E0','E1','F0','F1','G0','G1','H0','H1','I0','I1']
merged = Path(SRC) / 'merged.tsv'
files = [str(merged)] if merged.exists() else sorted(glob.glob(SRC + '/out/*.tsv'))
seen = {}
for fn in files:
    for l in open(fn):
        if l.startswith('#') or not l.strip():
            continue
        f = l.rstrip('\n').split('\t')
        if len(f) < 6 or f[3] == 'grade':
            continue
        m, g, chain = f[0], f[3], f[5]
        ch = re.sub(r'^\(last \d+\)\s*', '', chain)
        evs = ' '.join(x.split(':', 1)[1] for x in ch.split() if ':' in x and not x.startswith('b>k'))
        keep = g in ('LOOPER', 'MULTI', 'MULTI?', 'W1-HALTER', 'W1-HALT?', 'W1-LOOPER') or \
            (g in ('NOBOUNDARY', 'REBUILD') and re.search(r'R', re.sub(r'/\d+', '', evs)))
        if keep:
            p = m.split('_')
            und = [SL[2 * q + c] for q in range(len(p)) for c in range(2) if p[q][3 * c] == '-']
            seen[m] = (g, ','.join(und), f[4], ch[:300])
out = Path(__file__).with_name('rows.tsv')
with out.open('w') as fo:
    for m, (g, und, tmpl, ch) in seen.items():
        fo.write(f'{m}\t{g}\t{und}\t{tmpl}\t{ch}\n')
from collections import Counter
print(len(seen), 'rows from', len(files), 'files;', Counter(v[0] for v in seen.values()))
print('undefined-slot counts:', Counter(len(v[1].split(',')) for v in seen.values()))
