import sys, os, re, glob, collections
"""countdown.py DIR...: f_(w+1) signature search.  For every run file, collect J views ending in '1*K' (K >= KMIN) with
<= MAXTOK prefix tokens; group by shape (numbers >= 50 -> X).  Within a shape, look at consecutive occurrences: a prefix
number that DEcreases by a small constant d (1..30) at least 3 times in a row while K or the view changes = a counter that
is consumed once per round.  Also flags t decreasing.  Prints file, shape, position, values, Ks."""
KMIN = int(os.environ.get('KMIN', '150')); MAXTOK = int(os.environ.get('MAXTOK', '8'))
for d in sys.argv[1:]:
    for f in sorted(glob.glob(os.path.join(d, '*.txt'))):
        occ = collections.defaultdict(list)
        try: lines = open(f, errors='replace').readlines()
        except OSError: continue
        for l in lines:
            if not l.startswith('J') or '|' not in l: continue
            v = l.split('|', 1)[1].strip(); tk = v.split()
            if not tk or not tk[-1].startswith('1*'): continue
            try: K = int(tk[-1][2:])
            except: continue
            if K < KMIN or len(tk) - 1 > MAXTOK: continue
            pre = tk[:-1]
            if any(not re.match(r'^(\d+|\d+\*\d+|0\*\d+|z\d+)$', x) for x in pre): continue
            sh = ' '.join('X' if re.match(r'^\d+$', x) and int(x) >= 50 else x for x in pre)
            nums = [int(x) for x in pre if re.match(r'^\d+$', x) and int(x) >= 50]
            t = int(re.search(r' t=(\d+)', l).group(1)) if ' t=' in l else -1
            occ[sh].append((nums, K, t, l.split()[0]))
        for sh, L in occ.items():
            if len(L) < 4 or 'X' not in sh: continue
            n = len(L[0][0])
            for p in range(n):
                vals = [x[0][p] for x in L if len(x[0]) == n]; Ks = [x[1] for x in L if len(x[0]) == n]
                best = 0; cur = 0
                for i in range(1, len(vals)):
                    dd = vals[i - 1] - vals[i]
                    if 1 <= dd <= 30 and Ks[i] != Ks[i - 1]: cur += 1; best = max(best, cur)
                    else: cur = 0
                if best >= 3: print('%s | %s | pos %d | vals %s | K %s' % (os.path.basename(f), sh, p, vals[:12], Ks[:12]))
