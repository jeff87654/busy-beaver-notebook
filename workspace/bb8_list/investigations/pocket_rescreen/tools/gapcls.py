import sys, collections
out = open('gapcls_r1lg.tsv', 'w', newline='\n'); c = collections.Counter(); ex = {}
for l in open('gapsnap_r1lg.txt'):
    parts = l.strip().split(' | '); m = parts[0]; tail = parts[-1].split(); st = tail[-2]
    snaps = []
    for p in parts[1:]:
        f = p.split()[:4]; g = [int(x) for x in f[3].split(',')]
        snaps.append((int(f[0]), int(f[1]), int(f[2]), g))
    if st != 'RUN' or len(snaps) < 4: k = st + '-early'
    else:
        nb = [s[2] for s in snaps]; g1 = [s[3][0] for s in snaps]; r1 = [s[1] for s in snaps]
        if nb[-1] == 0: k = 'NOGAP(run-coded/other)'
        elif nb[-1] == 1 and nb[-2] == 1 and abs(g1[-1] - g1[-2]) <= max(4, g1[-2] // 10) and r1[-1] >= 2 * r1[0]:
            k = 'UNARY-GAP(1 big gap ~const, accumulator grows)'
        elif nb[-1] == 1 and g1[-1] > 1.5 * g1[-2]: k = 'GAP-GROWS'
        elif nb[-1] >= 2: k = 'MULTI-GAP(%s)' % ('const' if nb[-1] == nb[-2] else 'changing')
        else: k = 'OTHER'
    c[k] += 1; ex.setdefault(k, l.strip()[:230]); out.write('%s\t%s\n' % (m, k))
for k, v in c.most_common(): print(v, k); print('    e.g.', ex[k])
