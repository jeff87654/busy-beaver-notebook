import collections, sys
rows = collections.defaultdict(dict)
for l in open(sys.argv[1]):
    f = l.rstrip('\n').split('\t'); rows[f[0]][f[1]] = f[2:]
labs = sys.argv[2].split(',')
cls = collections.Counter(); groups = collections.defaultdict(list)
for m, d in rows.items():
    tags = []
    for lab in labs:
        k, st, jv, lj, hs, lmin, rmax, qmin, qmax = d[lab]
        jv, lmin, rmax, qmin, qmax = map(int, (jv, lmin, rmax, qmin, qmax))
        if k == 'H': tags.append('H')
        elif rmax > 200000 or lmin < -200000: tags.append('RUN')
        else: tags.append('J%d' % min(jv, 9))
    s = '/'.join(tags); cls[s] += 1
    groups[(s,) + tuple(d[l][4] for l in labs)].append(m)
for k, v in cls.most_common(): print(v, k)
print('groups', len(groups), 'non-RUN groups', sum(1 for k in groups if 'RUN' not in k[0]))
with open(sys.argv[3], 'w') as f:
    for k, ms in sorted(groups.items()):
        f.write(f'{k[0]}\t' + '\t'.join(k[1:]) + f'\t{len(ms)}\t' + ' '.join(ms) + '\n')
