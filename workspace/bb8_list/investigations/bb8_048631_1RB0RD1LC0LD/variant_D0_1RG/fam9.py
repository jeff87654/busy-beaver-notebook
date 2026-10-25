"""Families and the TL matcher for planner9 (1RB0RD_1LC0LD_1LA1RC_0LB0RE_1LF1RA_1LG---_0LH1LE_0LA0LB)."""
import planner9 as P
from planner9 import C, BLANK as BL

R0 = [1, 0, 0, 1, 1, BL]          # right part "100110 0^inf" with the head (state E) on its first cell


def bits(s):
    return tuple(int(c) for c in s)


def left_tokens(items, term=BL):
    """items: LEFT-TO-RIGHT list of (blockstring, count) with count an int (concrete copies) or an affine
    count C(...).  Returns the left stream (nearest the head first) ending in term."""
    out = []
    for b, c in reversed(items):
        blk = tuple(reversed(bits(b)))
        if isinstance(c, int):
            out.extend(list(blk) * c)
        else:
            out.extend(P.mkrun(blk, c))
    out.append(term)
    return P.norm_side(out)


def ecfg(items, term=BL):
    return ('E', left_tokens(items, term), list(R0), '>')


def PA(z, y, x):
    return ecfg([('001', z), ('000', 1), ('011', 1), ('110', 1), ('010', y), ('000', 1), ('111', 1), ('001', x),
                 ('000', 1), ('011', 1), ('111', 3), ('001', 1), ('100', 1)])


def PB(z, y, x):
    return ecfg([('100', z), ('001', 1), ('111', 1), ('001', y), ('000', 1), ('011', 1), ('001', x), ('000', 1),
                 ('011', 1), ('111', 14), ('001', 1), ('100', 1)])


def PC(z, y, x):
    return ecfg([('010', z), ('000', 1), ('111', 1), ('100', y), ('001', x), ('000', 1), ('011', 1), ('111', 47),
                 ('001', 1), ('100', 1)])


# ---------------------------------------------------------------- TL matcher
def take_cells(L, i, blk):
    k = 0
    n = len(blk)
    while all(isinstance(t, int) for t in L[i:i + n]) and tuple(L[i:i + n]) == blk:
        k += 1
        i += n
    return k, i


LOOPLOG = []


def m_TL(cfg):
    """TLs : c' = c + 3*b -> [0;0;1]^^c *> [1;1;1]^^b *> l {{E}}> R0 -->* [0;0;1]^^c' *> l {{E}}> R0"""
    q, L, R, mode = cfg
    if q != 'E' or mode != '>' or R != R0:
        return None
    b001 = (0, 0, 1)
    b111 = (1, 1, 1)
    pre = []
    # rotate a misaligned (100)-type run in front of the 111 part into the 001 phase
    for idx, t in enumerate(L):
        if P.is_run(t):
            if t[1] in ((0, 1, 0), (1, 0, 0)):
                r = P.realign(L, idx, b001)
                if r is None:
                    return None
                if P.count_runs(cfg, t[1], t[2]) != 1:
                    return None
                L, _, pre = r
            break
    k1, i = take_cells(L, 0, b001)
    crun = None
    if i < len(L) and P.is_run(L[i]) and L[i][1] == b001:
        crun = i
        i += 1
    k2, i = take_cells(L, i, b001) if crun is not None else (0, i)
    j1, i = take_cells(L, i, b111)
    texts = list(pre)
    side = list(L)
    if not (i < len(L) and P.is_run(L[i]) and L[i][1] == b111):
        if j1 == 0:
            return None
        # concrete 111 cells only: b is a numeral
        cstart = 0
        if crun is not None:
            for _ in range(k2):
                side, t = P.absorb_side(side, crun, 'far')
                texts.append(t)
            for _ in range(k1):
                side, t = P.absorb_side(side, crun, 'near')
                crun -= 3
                texts.append(t)
            ccnt = side[crun][2]
            ctxt = P.ccoq(ccnt)
            bstart = crun + 1
        else:
            ccnt = C(k1)
            ctxt = '%d' % k1
            bstart = 3 * k1
        rest = side[bstart + 3 * j1:]
        bcnt = C(j1)
        btxt = '%d' % j1
        newc = P.cadd(ccnt, P.cscale(bcnt, 3))
        newctxt = P.ccoq(newc)
        if not newc[1] and newc[0] <= P.SMALL:
            newctxt = '%d' % newc[0]
        newL = P.norm_side(P.mkrun(b001, newc) + rest)
        texts.append('follow (TLs %s %s %s %s ltac:(kN_lia)).' % (
            btxt, ctxt, newctxt, P.paren(P.side_coq(rest))))
        LOOPLOG.append((ccnt, bcnt))
        return (q, newL, R, mode), texts, 'TL c=%s b=%s (concrete)' % (P.cstr(ccnt), P.cstr(bcnt))
    brun = i
    i += 1
    j2, i = take_cells(L, i, b111)
    rest = L[i:]
    # absorb into the 111 run (near cells first, then far cells), then into the 001 run
    for _ in range(j1):
        side, t = P.absorb_side(side, brun, 'near')
        brun -= 3
        texts.append(t)
    for _ in range(j2):
        side, t = P.absorb_side(side, brun, 'far')
        texts.append(t)
    if crun is not None:
        for _ in range(k2):
            side, t = P.absorb_side(side, crun, 'far')
            texts.append(t)
            brun -= 3
        for _ in range(k1):
            side, t = P.absorb_side(side, crun, 'near')
            crun -= 3
            brun -= 3
            texts.append(t)
        ccnt = side[crun][2]
        assert crun == 0
    else:
        ccnt = C(k1)
        crun = None
    bcnt = side[brun][2]
    rest = side[brun + 1:]
    newc = P.cadd(ccnt, P.cscale(bcnt, 3))
    ctxt = P.ccoq(ccnt) if crun is not None else '%d' % k1
    newL = P.norm_side(P.mkrun(b001, newc) + rest)
    newcfg = (q, newL, R, mode)
    newctxt = P.ccoq(newc)
    if not newc[1] and newc[0] <= P.SMALL:
        newctxt = '%d' % newc[0]
    texts.append('follow (TLs %s %s %s %s ltac:(kN_lia)).' % (
        P.ccoq(bcnt), ctxt, newctxt, P.paren(P.side_coq(rest))))
    LOOPLOG.append((ccnt, bcnt))
    return newcfg, texts, 'TL c=%s b=%s' % (P.cstr(ccnt), P.cstr(bcnt))


m_TL.anytime = True
