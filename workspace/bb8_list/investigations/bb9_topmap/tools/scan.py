import sys, os; BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, BASE); import idle
"""scan.py: over runs/A_*/tree.tsv (+ run files), per machine: outcome, top views (shape -> K list, K >= 1000),
'arith' flag when the K differences are periodic with period <= 4 (+-20 = exact rebuild loop, non-halting shape), and
'growing tops' = number of tops whose K is not arithmetic.  Prints candidates (>= 2 non-arithmetic tops) sorted."""
import glob, re, collections
TOP = re.compile(r'^((?:\S+ )*?)1\*(\d+)$')
SH = re.compile(r'^(0\*\d+|0) (1 )?7 (z2 \d+ )?1\*(\d+)$')
rows = []
for tsv in glob.glob(os.path.join(BASE, 'runs', 'A_*', 'tree.tsv')):
    d = os.path.dirname(tsv)
    for l in open(tsv):
        p = l.rstrip('\n').split('\t'); mid, m, out = p[0], p[1], p[2]
        f = os.path.join(d, mid + '.txt')
        if not os.path.exists(f): continue
        tops = collections.OrderedDict()
        for x in open(f, errors='replace'):
            if x.startswith('J') and '|' in x:
                v = x.split('|', 1)[1].strip(); mm = TOP.match(v)
                if mm and int(mm.group(2)) >= 1000 and len(mm.group(1).split()) <= 5:
                    shape = re.sub(r'\d{3,}', 'X', mm.group(1)) + '1*K'; tops.setdefault(shape, []).append(int(mm.group(2)))
        for shape, ks in tops.items():
            dif = [b - a for a, b in zip(ks, ks[1:])]
            arith = any(len(dif) >= p + 1 and all(abs(dif[i] - dif[i - p]) <= 20 for i in range(p, len(dif))) for p in (1, 2, 3, 4))
            rows.append((0 if arith else len(ks), os.path.basename(d), m, out, shape, ks, 'ARITH' if arith else ''))
for r in sorted(rows, key=lambda r: -r[0]):
    if len(r[5]) >= 2: print(r[0], r[1], r[2], r[3], repr(r[4]), r[5][:10], r[6])
