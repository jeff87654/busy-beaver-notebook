"""Matchers for the two transfer loops (both consume ALL their source blocks).
TAloop: [0;1;0;1]^^n *> 0>>0>>1>>0>> [1;0;1;0]^^k *> l {{F}}> 1>>0>>0>>0>> const 0
        -->* [0;1;0;1]^^(n+6k) *> 0>>0>>1>>0>> l {{F}}> 1>>0>>0>>0>> const 0
TBloop: [1;0;1;0]^^m *> [0;1;0;1]^^k *> l {{H}}> 0>>1>>0>>0>> const 0
        -->* [1;0;1;0]^^(m+6k) *> l {{H}}> 0>>1>>0>>0>> const 0
Counts: concrete copies plus at most one run (linear form)."""
import planner8 as P
BL = P.BLANK
STOP_SYMBOLIC = False
STOP_ALL = False

def take(L, i, blk):
    """count concrete copies of blk at L[i:], then an optional run of blk; returns (conc, runcnt, newi)"""
    b = list(blk); c = 0
    while L[i:i + 4] == b:
        c += 1; i += 4
    rc = ()
    if i < len(L) and P.is_run(L[i]) and L[i][1] == tuple(blk):
        rc = L[i][2]; i += 1
    return c, rc, i

def lin_scale(c, k):
    return tuple((v, k * a) for v, a in c)

def mk(blk, conc, rc):
    out = list(blk) * conc
    if rc:
        out.append(('run', tuple(blk), rc))
    return out

def cstr(conc, rc):
    parts = []
    for v, a in rc:
        parts.append(v if a == 1 else '%d * %s' % (a, v))
    if conc or not parts:
        parts.append(str(conc))
    return '(' + ' + '.join(parts) + ')'

def m_TA(cfg):
    q, L, R, mode = cfg
    if q != 'F' or mode != '>' or R != [1, BL]:
        return None
    n0, nr, i = take(L, 0, (0, 1, 0, 1))
    if L[i:i + 4] != [0, 0, 1, 0]:
        return None
    k0, kr, j = take(L, i + 4, (1, 0, 1, 0))
    if k0 == 0 and not kr:
        return None
    newc = n0 + 6 * k0
    newr = P.lin_add(nr, lin_scale(kr, 6)) if (nr or kr) else ()
    newL = mk((0, 1, 0, 1), newc, newr) + [0, 0, 1, 0] + L[j:]
    # Coq: follow (TAloop k n l) with the exact split used here
    frag = ('TA', cstr(k0, kr), cstr(n0, nr))
    if STOP_ALL or (STOP_SYMBOLIC and (kr or nr)):
        frag = ('STOP',) + frag + (n0, nr, k0, kr, i, j)
    return (q, P.norm_side(newL), R, mode), frag, 'TAloop k=%s n=%s' % (cstr(k0, kr), cstr(n0, nr))
m_TA.anytime = True

def m_TB(cfg):
    q, L, R, mode = cfg
    if q != 'H' or mode != '>' or R != [0, 1, BL]:
        return None
    m0, mr, i = take(L, 0, (1, 0, 1, 0))
    k0, kr, j = take(L, i, (0, 1, 0, 1))
    if k0 == 0 and not kr:
        return None
    newc = m0 + 6 * k0
    newr = P.lin_add(mr, lin_scale(kr, 6)) if (mr or kr) else ()
    newL = mk((1, 0, 1, 0), newc, newr) + L[j:]
    frag = ('TB', cstr(k0, kr), cstr(m0, mr))
    if STOP_ALL or (STOP_SYMBOLIC and (kr or mr)):
        frag = ('STOP',) + frag + (m0, mr, k0, kr, i, j)
    return (q, P.norm_side(newL), R, mode), frag, 'TBloop k=%s m=%s' % (cstr(k0, kr), cstr(m0, mr))
m_TB.anytime = True


def m_rot(cfg):
    """At a loop position, move concrete cells that sit between the leading copies of the loop block and a run
    of a rotation of that block to the far side of the run:  pre ++ (suffix ++ pre)^^n = (pre ++ suffix)^^n ++ pre.
    Coq: one [rewrite (rot4 a b c d n)] per moved cell, rot4 : a >> [b;c;d;a]^^n *> r = [a;b;c;d]^^n *> a >> r."""
    q, L, R, mode = cfg
    if mode != '>':
        return None
    if q == 'F' and R == [1, BL]:
        blk = (0, 1, 0, 1)
    elif q == 'H' and R == [0, 1, BL]:
        blk = (1, 0, 1, 0)
    else:
        return None
    i = 0
    while L[i:i + 4] == list(blk):
        i += 4
    for plen in (1, 2, 3):
        pre = L[i:i + plen]
        if len(pre) < plen or not all(isinstance(t, int) for t in pre):
            break
        if i + plen < len(L) and P.is_run(L[i + plen]):
            rb, cnt = L[i + plen][1], L[i + plen][2]
            if len(rb) == 4 and tuple(rb[4 - plen:]) == tuple(pre) and tuple(pre) + tuple(rb[:4 - plen]) == blk:
                assert len(cnt) == 1 and cnt[0][1] == 1
                v = cnt[0][0]
                frags = []
                cur = tuple(rb)
                for t in range(plen - 1, -1, -1):
                    a = pre[t]
                    assert cur[3] == a
                    frags.append('rewrite (rot4 %d %d %d %d %s).' % (a, cur[0], cur[1], cur[2], v))
                    cur = (a,) + cur[:3]
                assert cur == blk
                newL = L[:i] + [('run', blk, cnt)] + list(pre) + L[i + plen + 1:]
                return (q, P.norm_side(newL), R, mode), ' '.join(frags), 'rotate %d cells past run %s' % (plen, v)
    return None
m_rot.anytime = True
