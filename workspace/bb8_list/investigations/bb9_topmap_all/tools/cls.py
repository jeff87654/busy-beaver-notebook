import sys, os, re, collections
"""cls.py TSV RUNDIR [KMIN]: classify each screened machine from its run file.
 tops = J views '<=5 prefix tokens 1*K' with K >= KMIN (shape = prefix with numbers >= 100 -> X); main shape = most tops.
 type: HALT-n (halted after n main-shape tops) | ARITH (main tops arithmetic, period<=4) [+T if t changes between tops]
       | GROW-n (>= 2 main tops, not arithmetic) | NOTOP | other.  Writes TSV.cls with: id machine outcome type ntops shape Ks ts."""
TSV, RD = sys.argv[1], sys.argv[2]; KMIN = int(sys.argv[3]) if len(sys.argv) > 3 else 200
TOP = re.compile(r'^((?:\S+ )*?)1\*(\d+)$')
def ana(f):
    J = []
    if not os.path.exists(f): return None
    for x in open(f, errors='replace'):
        if x.startswith('J') and '|' in x:
            mt = re.search(r' t=(\d+)', x); J.append((x.split('|', 1)[1].strip(), int(mt.group(1)) if mt else -1))
    tops = collections.OrderedDict()
    for v, t in J:
        mm = TOP.match(v)
        if mm and int(mm.group(2)) >= KMIN and len(mm.group(1).split()) <= 5:
            tops.setdefault(re.sub(r'\d{3,}', 'X', mm.group(1)).strip(), []).append((int(mm.group(2)), t))
    if not tops: return ('', [], [])
    sh, ks = max(tops.items(), key=lambda kv: len(kv[1]))
    # collapse repeated K (same top seen in several views)
    K = []; T = []
    for k, t in ks:
        if not K or k != K[-1]: K.append(k); T.append(t)
    return sh, K, T
out = open(TSV + '.cls', 'w')
for l in open(TSV):
    p = l.rstrip('\n').split('\t'); mid, m, res = p[0], p[1], p[2]
    a = ana(os.path.join(RD, mid + '.txt'))
    if a is None: typ = 'NOFILE'; sh, K, T = '', [], []
    else:
        sh, K, T = a
        dif = [b - c for c, b in zip(K, K[1:])]
        arith = len(K) >= 3 and any(len(dif) >= q + 1 and all(abs(dif[i] - dif[i - q]) <= 20 for i in range(q, len(dif))) for q in (1, 2, 3, 4))
        tch = len(set(T)) > 1
        if not K: typ = 'NOTOP'
        elif arith: typ = 'ARITH' + ('+T' if tch else '')
        elif res.startswith('HALT'): typ = 'HALT-%d' % len(K)
        elif len(K) >= 2: typ = 'GROW-%d' % len(K) + ('+T' if tch else '')
        else: typ = 'ONE'
    out.write('\t'.join([mid, m, res, typ, str(len(K)), sh, ','.join(map(str, K[:20])), ','.join(map(str, T[:20]))]) + '\n')
out.close()
c = collections.Counter(x.split('\t')[3].split('-')[0] + ('-' + x.split('\t')[3].split('-')[1] if x.split('\t')[3].startswith(('HALT-', 'GROW-')) else '') for x in open(TSV + '.cls'))
print(sorted(c.items()))
