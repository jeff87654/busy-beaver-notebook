import sys, re
for l in open(sys.argv[1]):
    f = l.rstrip('\n').split('\t')
    if len(f) < 4: continue
    m, kind, n, s = f
    toks = s.split()
    pairs = [(int(a), int(b)) for a, b in (t.split(':') for t in toks if re.match(r'^\d+:\d+$', t))]
    if not pairs: continue
    c6 = [p[0] for p in pairs]; z = [p[1] for p in pairs]
    tail = ' '.join(toks[-3:])
    g = m.split('1LC0RG_')[1]; e0 = m.split('1RA1LE_')[1][:3]
    print(f'{e0} {g}\t{kind}\tn={len(pairs)}\tc6:{c6[0]}->{min(c6)}..{c6[-1]}\tz:{z[0]}->{max(z)}..{z[-1]}\t{tail[:60]}')
