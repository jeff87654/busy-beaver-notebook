import sys, collections
OLD = {'b6r20': 42430, 'b11r20': 82054, 'b16r20': 132046, 'b6r380': 1102990}
rows = collections.defaultdict(dict)
for l in open(sys.argv[1]):
    f = l.rstrip('\n').split('\t')
    if f[2] == 'BAD': raise SystemExit('BAD ' + l)
    rows[f[0]][f[1]] = f[2:]
labs = list(OLD)
cls = collections.Counter(); out = []
for m, d in rows.items():
    assert set(d) == set(labs), m
    sig = []
    for lab in labs:
        r = d[lab]
        if r[0] == 'H':
            extra = int(r[1]) - OLD[lab]
            sig.append('h' if extra < 0 else ('q' if extra < 100000 else 'L'))
        else: sig.append(r[0])
    s = ''.join(sig); cls[s] += 1; out.append((s, m, ' '.join('/'.join(d[l]) for l in labs)))
for k, v in cls.most_common(): print(v, k)
with open(sys.argv[2], 'w') as f:
    for s, m, det in sorted(out): f.write(f'{s}\t{m}\t{det}\n')
