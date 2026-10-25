import sys, os, re, glob
"""p2scan.py DIR: per run file: outcome, #jumps, tops per shape (K >= 1000, <= 5 prefix tokens), periodic-arith flag."""
TOP = re.compile(r'^((?:\S+ )*?)1\*(\d+)$')
for f in sorted(glob.glob(os.path.join(sys.argv[1], '*.txt'))):
    J = []; out = 'RUNNING'
    for x in open(f, errors='replace'):
        if x.startswith('J') and '|' in x: J.append(x.split('|', 1)[1].strip())
        elif x.startswith(('HALT', 'STOP', 'END', 'KILLED')): out = ' '.join(x.split()[:2]) + ((' ones ' + x.split('ones ')[1].split()[0]) if 'ones' in x else '')
    tops = {}
    for v in J:
        mm = TOP.match(v)
        if mm and int(mm.group(2)) >= 1000 and len(mm.group(1).split()) <= 5:
            tops.setdefault(re.sub(r'\d{3,}', 'X', mm.group(1)), []).append(int(mm.group(2)))
    best = max(tops.items(), key=lambda kv: len(kv[1]), default=('', []))
    ks = best[1]; dif = [b - a for a, b in zip(ks, ks[1:])]
    arith = any(len(dif) >= q + 1 and all(abs(dif[i] - dif[i - q]) <= 20 for i in range(q, len(dif))) for q in (1, 2, 3, 4))
    print('%-28s %-22s J%-3d %-3d %s %r %s' % (os.path.basename(f)[:-4], out, len(J), len(ks), 'ARITH' if arith else '-', best[0], ks[:12]))
