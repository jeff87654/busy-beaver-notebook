"""canon.py: canonical form of a TM under state relabelling (BFS order from the start state A) and mirroring."""
def parse(m):
    rows = m.split('_')
    return [[None if r[3*c] == '-' else (r[3*c], r[3*c+1], ord(r[3*c+2]) - 65) for c in (0, 1)] for r in rows]
def canon1(t, start=0, mir=False):
    order = [start]; i = 0
    while i < len(order):
        for c in (0, 1):
            v = t[order[i]][c]
            if v is not None and v[2] not in order and 0 <= v[2] < len(t):
                order.append(v[2])
        i += 1
    for s in range(len(t)):
        if s not in order: order.append(s)
    pos = {s: k for k, s in enumerate(order)}
    out = []
    for s in order:
        row = ''
        for c in (0, 1):
            v = t[s][c]
            if v is None: row += '---'
            else:
                d = v[1]
                if mir: d = 'L' if d == 'R' else 'R'
                row += v[0] + d + chr(65 + pos[v[2]])
        out.append(row)
    return '_'.join(out)
def canon(m):
    t = parse(m)
    return min(canon1(t, 0, False), canon1(t, 0, True))
