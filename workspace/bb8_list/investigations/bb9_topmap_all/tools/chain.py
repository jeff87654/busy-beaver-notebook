import sys, os, re, glob
"""chain.py DIR...: per run file, the '0*2 7 1*K' tops (K>=KMIN env, default 150) with t; 'short chain' = maximal run of
consecutive tops whose t differs by <= 3 per step (h003-like short rounds).  Prints file, #tops, best chain length, chain."""
KMIN = int(os.environ.get('KMIN', '150')); TOP = re.compile(r'\| 0\*2 7 1\*(\d+)$')
res = []
for d in sys.argv[1:]:
    for f in glob.glob(os.path.join(d, '*.txt')):
        tops = []
        for l in open(f, errors='replace'):
            if l.startswith('J'):
                m = TOP.search(l.rstrip())
                if m and int(m.group(1)) >= KMIN: tops.append((int(m.group(1)), int(re.search(r' t=(\d+)', l).group(1)), l.split()[0]))
        best = []; cur = []
        for x in tops:
            if cur and 0 < x[1] - cur[-1][1] <= 3: cur.append(x)
            else: cur = [x]
            if len(cur) > len(best): best = list(cur)
        res.append((len(best), len(tops), f, best))
for b, n, f, ch in sorted(res, reverse=True)[:int(os.environ.get('TOPN', '40'))]:
    print(b, n, f, ' '.join('%d/t%d' % (k, t) for k, t, j in ch))
