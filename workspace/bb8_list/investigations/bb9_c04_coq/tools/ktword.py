"""ktword.py: build the cell word of a Kt spec (same format as tmsim/c04raw)."""
def build(spec):
    f = spec.split(';'); out = []
    if f[0]:
        for it in f[0].split(','):
            rep = 1
            if '*' in it: it, rep = it.split('*'); rep = int(rep)
            for _ in range(rep):
                if it[0] == 'z': out += [0] * int(it[1:])
                else: out += [1, 0] * int(it) + [1]
    m, r, t = int(f[1]), int(f[2]), int(f[3])
    out += [1, 0] * m + [1] + [1, 0] * r + [1, 1] + [1, 1, 1, 1, 1, 1, 0, 0] * t + [1, 0, 0, 1]
    return ''.join(map(str, out))
