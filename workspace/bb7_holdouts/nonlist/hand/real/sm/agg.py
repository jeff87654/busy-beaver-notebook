import glob, collections
res = collections.defaultdict(dict)
for f in glob.glob('s_K*_m*.tsv'):
    K, m = f[3:-4].split('_m'); K = K
    for l in open(f):
        x = l.rstrip('\n').split('\t')
        if len(x) < 3 or x[0] in ('machine',) or x[0].startswith('#'): continue
        res[x[0]][(int(K), int(m))] = x[2]
mem = [l.rstrip('\n').split('\t') for l in open('../members.tsv')]
out = open('smsum.tsv', 'w')
for f in mem:
    r = res[f[2]]
    byK = {}
    for K in (2, 3, 4, 6):
        hs = [m for (k, m), v in sorted(r.items()) if k == K and v == 'HALT']
        n = sum(1 for (k, m) in r if k == K)
        byK[K] = (len(hs), n, hs)
    tot = sum(v[0] for v in byK.values()); n = sum(v[1] for v in byK.values())
    cls = 'NONE' if tot == 0 else ('ALL' if tot == n else 'MIXED')
    perK = ' '.join(f'K{K}:{byK[K][0]}/{byK[K][1]}' for K in byK)
    mixK = [K for K in byK if 0 < byK[K][0] < byK[K][1]]
    out.write(f'{f[0]}\t{f[2]}\t{cls}\t{perK}\t' + ';'.join(f'K{K}h=' + ','.join(map(str, byK[K][2])) for K in mixK) + '\n')
