"""canon(m): canonical relabelling (BFS from A over transitions in order (state,0),(state,1)); unreachable states dropped
-> returns (canonical string over reachable states, n_reachable).  Isomorphic machines get the same string."""
def canon(m):
    rows = m.split('_'); n = len(rows)
    tr = {}
    for s in range(n):
        for c in range(2):
            x = rows[s][3 * c:3 * c + 3]; tr[(s, c)] = None if x[2] in '-' or ord(x[2]) - 65 >= n else (x[0], x[1], ord(x[2]) - 65)
            if x[2] == '-' : tr[(s, c)] = None
    lab = {0: 0}; order = [0]; i = 0
    while i < len(order):
        s = order[i]; i += 1
        for c in range(2):
            t = tr[(s, c)]
            if t and t[2] not in lab: lab[t[2]] = len(order); order.append(t[2])
    out = []
    for s in order:
        r = ''
        for c in range(2):
            t = tr[(s, c)]; r += '---' if t is None else t[0] + t[1] + chr(65 + lab[t[2]])
        out.append(r)
    return '_'.join(out), len(order)
