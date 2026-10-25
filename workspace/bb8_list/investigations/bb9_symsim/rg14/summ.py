# summ.py : classify the v14 regrade outputs (rg14/out_*.txt)
import glob, collections, re
rows = {}
for f in sorted(glob.glob('rg14/out_*.txt')) + sorted(glob.glob('rg14/nc_out_*.txt')):
    for l in open(f):
        p = l.split(); m = p[0]
        if len(p) < 2: continue
        d = {k: v for k, v in (x.split('=', 1) for x in p if '=' in x and x.split('=', 1)[0] in ('kj', 'bc', 'sc', 'it', 'its', 'aff', 'macro', 'rcu'))}
        rec = (p[1], d, l.rstrip('\n'), f)
        old = rows.get(m)
        def rank(r):
            v, dd = r[0], r[1]
            return (v in ('HALT', 'CYCLE'), int(dd.get('bc', 0) or 0) + int(dd.get('sc', 0) or 0) + int(dd.get('its', 0) or 0))
        if old is None or rank(rec) > rank(old): rows[m] = rec
src = {}
for l in open('rg14/list_591.txt'): src[l.split()[0].strip()] = '591'
for l in open('rg14/list_memcap4.txt'): src[l.split()[0].strip()] = 'memcap4'
for l in open('rg14/list_cs97.txt'): src[l.split()[0].strip()] = 'cs97'
C = collections.Counter(); flags = []
for m, (v, d, l, f) in rows.items():
    bc, sc, its = int(d.get('bc', 0) or 0), int(d.get('sc', 0) or 0), int(d.get('its', 0) or 0)
    # rcu = pass/fail/unchecked counts of the rules used on the main path (+ kinds of the non-passing ones)
    rc = d.get('rcu', '0/0/0').split(','); nf, nu = (int(x) for x in rc[0].split('/')[1:3]) if rc[0].count('/') == 2 else (0, 1)
    star = '' if nf == 0 and nu == 0 else '*'
    why = ('[' + ','.join(rc[1:]) + ']') if star else ''
    if v == 'HALT': cls = 'HALT' + star + (' big>=2' if bc >= 2 else (' big=1' if bc == 1 else ' fixed-depth')) + why
    elif v == 'CYCLE': cls = 'NONHALT' + star + ' (CYCLE)' + why
    elif v == 'BUDGET' and bc >= 1: cls = 'BUDGET f_w-depth rounds (looper shape)'
    elif v == 'BUDGET' and sc >= 1: cls = 'BUDGET counter loop C(j,2X+2,0)'
    elif v == 'BUDGET' and its >= 1: cls = 'BUDGET ITER (symbolic k)'
    else: cls = v + ' other'
    C[(src.get(m, '?'), cls)] += 1
    if v == 'HALT' and bc >= 2: flags.append(l)
    if v == 'BUDGET' and its >= 1 and (bc >= 1 or sc >= 1): flags.append('OUTERLOOP? ' + l)
for k in sorted(C): print(f'{C[k]:5d}  {k[0]:8s} {k[1]}')
print(len(rows), 'machines'); [print('FLAG', x[:300]) for x in flags]
