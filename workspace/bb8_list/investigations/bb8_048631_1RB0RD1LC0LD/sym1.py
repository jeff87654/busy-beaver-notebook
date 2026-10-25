import planner8 as P
TM = "1RB0RD_1LC0LD_1LA1RC_0LB0RE_1LF1RA_1LG---_0LH1LE_0LA0LB"
P.set_tm(TM)
BL = P.BLANK
def bits(s): return [int(c) for c in s]
def side_from_ltr(items, left):
    """items: list of (blockstring, count) in LEFT-TO-RIGHT order; count int or (var, const).
    returns stream-order token list (nearest head first) WITHOUT terminator."""
    toks = []
    for b, c in items:
        if isinstance(c, int):
            toks.append(('lit', bits(b) * c))
        else:
            v, k = c
            toks.append(('run', b, v, k))
    out = []
    seq = list(reversed(toks)) if left else toks
    for t in seq:
        if t[0] == 'lit':
            cells = t[1]
            out.extend(reversed(cells) if left else cells)
        else:
            _, b, v, k = t
            blk = tuple(reversed(bits(b))) if left else tuple(bits(b))
            # constant copies go nearest to the head
            if left:
                for _ in range(k): out.extend(blk)
                out.append(('run', blk, ((v, 1),)))
            else:
                for _ in range(k): out.extend(blk)
                out.append(('run', blk, ((v, 1),)))
    return out
def cfg(q, mode, left, right, lterm=BL, rterm=BL):
    return (q, P.norm_side(side_from_ltr(left, True) + [lterm]), P.norm_side(side_from_ltr(right, False) + [rterm]), mode)

PA = lambda z, y, x, zk=0, yk=0, xk=0: cfg('E', '>', [('001', (z, zk)), ('000', 1), ('011', 1), ('110', 1), ('010', (y, yk)), ('000', 1), ('111', 1), ('001', (x, xk)), ('000', 1), ('011', 1), ('111', 3), ('001', 1), ('100', 1)], [('100', 1), ('110', 1)])
if __name__ == '__main__':
    c = PA('z', 'y', 'x', 1, 8, 5)
    print(P.show(c))
    P.drive('PA', c, maxev=60)
