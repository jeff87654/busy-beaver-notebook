import sys, os, re, collections
"""mk_s3.py: stage-3 list from runs/w2.tsv.cls.  Candidates: not HALT/NOTOP/NOFILE/STOP_NEEDK and not plain ARITH (t const);
plus HALT with >= 2 tops.  Groups by W2 skeleton (zeros line + t sequence + outcome); writes runs/s3_reps.txt (one rep per
group, 'id machine'), runs/s3_groups.tsv (rep, size, members, skeleton)."""
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = [l.rstrip('\n').split('\t') for l in open(os.path.join(BASE, 'runs', 'w2.tsv.cls'))]
cand = []
for r in rows:
    mid, m, res, typ = r[:4]
    if typ in ('NOTOP', 'NOFILE') or res == 'STOP_NEEDK': continue
    if typ == 'ARITH' : continue
    if res.startswith('HALT') and int(r[4]) < 2: continue
    cand.append(r)
grp = collections.OrderedDict()
for r in cand:
    f = os.path.join(BASE, 'runs', 'W2', r[0] + '.txt'); z = ''; ts = []; end = ''
    for l in open(f, errors='replace'):
        if l.startswith('zeros:'): z = l[6:].strip()
        elif l.startswith('J'):
            mt = re.search(r' t=(\d+)', l); ts.append(mt.group(1) if mt else '')
        elif l.startswith(('HALT', 'STOP', 'END')): end = l.split()[0] + ' ' + l.split()[1]
    key = z + '|' + ','.join(ts) + '|' + end
    grp.setdefault(key, []).append(r)
with open(os.path.join(BASE, 'runs', 's3_reps.txt'), 'w') as f, open(os.path.join(BASE, 'runs', 's3_groups.tsv'), 'w') as g:
    for key, v in grp.items():
        f.write('%s %s\n' % (v[0][0], v[0][1]))
        g.write('\t'.join([v[0][0], str(len(v)), v[0][3], ','.join(x[0] for x in v), key[:300]]) + '\n')
print(len(cand), 'candidates,', len(grp), 'groups', collections.Counter(r[3].split('-')[0] for r in cand))
