import idle, sys
# usage: mk.py TEMPLATE K "ds a b"  -> init line for ms.exe (original orientation)
t, K, cfg = sys.argv[1], int(sys.argv[2]), sys.argv[3].split()
f = t.split(','); d = {}
for x in f[2:]:
    k, v = x.split('=', 1); d[k] = v
O, Q = f[0], f[1]
P = '' if d['P'] == '-' else d['P']; u = d['u']; s = d['s']; S = '' if d['S'] == '-' else d['S']
al, be = map(int, d['d'].split('d+')); aB, bB = map(int, d['b'].split('b+'))
ds = [] if cfg[0] == '-' else [int(x) for x in cfg[0].split(',')]
a, b = int(cfg[1]), int(cfg[2])
w = P
for x in ds: w += u * (al * x + be) + s
w += u * (al * a + be) + s + u * (aB * b + bB) + S
# mirrored machine: head on blank right of w. Original machine orientation: if O=='L', original = reverse, head on blank left.
if O == 'L':
    bits = '0' + w[::-1]   # head cell first
    while len(bits) % K: bits += '0'
    blocks = [bits[i:i+K] for i in range(0, len(bits), K)]
    print(Q, 0, '| [' + blocks[0] + ']', ' '.join(blocks[1:]))
else:
    bits = w + '0'
    while len(bits) % K: bits = '0' + bits
    blocks = [bits[i:i+K] for i in range(0, len(bits), K)]
    print(Q, K - 1, '|', ' '.join(blocks[:-1]), '[' + blocks[-1] + ']')
