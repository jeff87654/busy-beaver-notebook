import sys, os, re, glob, collections
"""ana.py RUNDIR [TSV]: per run file: outcome, #J, tops per shape (K>=1000, <=5 prefix tokens; numbers >=100 in prefix -> X),
t at each top, ARITH flag (K diffs periodic, period<=4, tol 20), and a 'grow' score = #tops of the best shape.
Prints rows with >= 2 tops in a shape, sorted by (non-arith, #tops)."""
TOP = re.compile(r'^((?:\S+ )*?)1\*(\d+)$')
rows = []; KMIN = int(os.environ.get("KMIN", "1000"))
for f in sorted(glob.glob(os.path.join(sys.argv[1], '*.txt'))):
    J = []; out = 'RUNNING'
    for x in open(f, errors='replace'):
        if x.startswith('J') and '|' in x:
            mt = re.search(r' t=(\d+)', x); J.append((x.split('|', 1)[1].strip(), int(mt.group(1)) if mt else -1))
        elif x.startswith(('HALT', 'STOP', 'END', 'KILLED')): out = ' '.join(x.split()[:2]) + ((' ones ' + x.split('ones ')[1].split()[0]) if 'ones' in x else '')
    tops = collections.OrderedDict()
    for v, t in J:
        mm = TOP.match(v)
        if mm and int(mm.group(2)) >= KMIN and len(mm.group(1).split()) <= 5:
            tops.setdefault(re.sub(r'\d{3,}', 'X', mm.group(1)).strip(), []).append((int(mm.group(2)), t))
    for sh, ks in tops.items():
        K = [k for k, t in ks]; dif = [b - a for a, b in zip(K, K[1:])]
        arith = any(len(dif) >= q + 1 and all(abs(dif[i] - dif[i - q]) <= 20 for i in range(q, len(dif))) for q in (1, 2, 3, 4))
        rows.append((not arith, len(K), os.path.basename(f)[:-4], out, len(J), sh, ks[:12], 'ARITH' if arith else '-'))
for r in sorted(rows, key=lambda r: (r[0], r[1]), reverse=True):
    if r[1] >= 2: print('%-7s %-22s J%-3d %-6s %-28r %s' % (r[2], r[3][:22], r[4], r[7], r[5], ' '.join('%d/t%d' % kt for kt in r[6])))
