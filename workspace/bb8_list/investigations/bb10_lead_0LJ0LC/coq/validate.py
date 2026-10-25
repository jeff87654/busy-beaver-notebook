"""Check symbolic transitions of engine.py against exact literal simulation with concrete parameter values.

concretize(cfg, values) turns a symbolic configuration into a concrete tape (VAR sides become a fixed marker word
that the machine must not touch); reaches(start, end, values) simulates the machine from the concrete start and
reports whether it passes through the concrete end configuration.
"""
from planner8 import T as TABLE, BLANK, is_run


MARK = (1, 0, 1, 1, 0, 0, 1, 1, 1, 0)      # stands for a VAR side; reading into it means the symbolic run was wrong


def side_cells(side, values):
    out, var = [], None
    for t in side:
        if isinstance(t, int):
            out.append(t)
        elif is_run(t):
            n = sum(c * values[k] for k, c in t[2])
            out.extend(list(t[1]) * n)
        elif t == BLANK:
            break
        else:                       # ('VAR', name)
            var = t[1]
            out.extend(MARK)
            break
    return out, var


def concretize(cfg, values):
    """(state, cells left of head nearest-first, head symbol, cells right nearest-first)."""
    q, L, R, mode = cfg
    l, _ = side_cells(L, values)
    r, _ = side_cells(R, values)
    if mode == '>':
        h, r = (r[0], r[1:]) if r else (0, r)
    else:
        h, l = (l[0], l[1:]) if l else (0, l)
    return q, l, h, r


def strip(cells):
    cells = list(cells)
    while cells and cells[-1] == 0:
        cells.pop()
    return cells


def same(c1, c2):
    return c1[0] == c2[0] and c1[2] == c2[2] and strip(c1[1]) == strip(c2[1]) and strip(c1[3]) == strip(c2[3])


def reaches(start, end, values, max_steps=2_000_000):
    q, l, h, r = concretize(start, values)
    goal = concretize(end, values)
    l, r = list(l), list(r)
    for n in range(max_steps):
        if same((q, l, h, r), goal):
            return n
        tr = TABLE.get((q, h))
        if tr is None:
            return None
        w, d, q = tr
        if d == 1:
            l.insert(0, w)
            h = r.pop(0) if r else 0
        else:
            r.insert(0, w)
            h = l.pop(0) if l else 0
    return None
