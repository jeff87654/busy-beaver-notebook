"""msim.py : small sound symbolic macro simulator (shift rules) for F89 in ORIGINAL orientation.
tape = list of items: '0'/'1' literal cells, or ['B', w, n] block (w repeated n times, n = Lin over symbols with lower bounds).
Shift rule: head in state q moving into a block from one side; simulate the machine literally on ONE copy of w entered from
that side; if it leaves through the opposite side in the same state q (writing w'), then by induction on n the whole block
becomes w'^n and the head leaves in state q (sound for every n >= 0).  Otherwise one copy is peeled off (needs n>=1 provable
from lower bounds) and simulated literally.  Symbols: LB[name] = lower bound (all symbols are naturals >= LB)."""
import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\never_audit')
from sym import Lin
M = '1RB0RE_0RC---_1LD0RG_1RA0RF_1LF0LD_1LD0LE_1RC1RE'


def parse(m):
    T = {}
    for q, g in enumerate(m.split('_')):
        for s in range(2):
            t = g[3 * s:3 * s + 3]
            T[(chr(65 + q), str(s))] = None if t[2] == '-' else (t[0], 1 if t[1] == 'R' else -1, t[2])
    return T


class Fail(Exception):
    pass


LB = {}


def lb(n):
    v = n.d.get('', 0)
    for k, c in n.d.items():
        if k == '':
            continue
        if c < 0:
            raise Fail('negative coef %r' % n)
        v += c * LB[k]
    return v


def copy_sim(T, w, q, frm):
    cells = list(w)
    h = 0 if frm == 'L' else len(w) - 1
    for _ in range(10000):
        tr = T[(q, cells[h])]
        if tr is None:
            return None
        cells[h] = tr[0]
        h += tr[1]
        q = tr[2]
        if h < 0:
            return ('L', q, ''.join(cells))
        if h >= len(w):
            return ('R', q, ''.join(cells))
    return None


CTXC = {}


def ctx_shift(T, w, ctx, q, dirn):
    """carried-context shift. dirn='L': segment = w+ctx, head at len(w) (ctx start) in q; success if the head comes back
    to index 0 in state q with seg[:len(ctx)]==ctx without leaving the segment -> returns w2 (seg[len(ctx):]).
    dirn='R': segment = ctx+w, head at len(ctx)-1 in q; success if head reaches len(w)+len(ctx)-1 in q with
    seg[len(w):]==ctx -> returns w2 = seg[:len(w)]."""
    key = (w, ctx, q, dirn)
    if key in CTXC:
        return CTXC[key]
    L = len(ctx)
    if dirn == 'L':
        seg = list(w + ctx); h = len(w); goal = 0
    else:
        seg = list(ctx + w); h = L - 1; goal = len(w) + L - 1
    res = None
    st = q
    for i in range(400):
        tr = T[(st, seg[h])]
        if tr is None:
            break
        seg[h] = tr[0]; h += tr[1]; st = tr[2]
        if h < 0 or h >= len(seg):
            break
        if h == goal and st == q:
            s2 = ''.join(seg)
            if dirn == 'L' and s2[:L] == ctx:
                res = s2[L:]
            if dirn == 'R' and s2[len(w):] == ctx:
                res = s2[:len(w)]
            break
    CTXC[key] = res
    return res


class Sim:
    def __init__(s, items, h, q, m=M):
        s.T = parse(m)
        s.t = [x if isinstance(x, str) else ['B', x[1], x[2]] for x in items]
        s.h = h
        s.q = q
        s.steps = 0
        s.macro = 0

    def step(s):
        t = s.t
        h = s.h
        # carried-context shifts (block word optionally regrouped as w^p, remainder copies put on the far side)
        def regroup(n, p):
            if p == 1:
                return n, 0
            coefs = [c for k2, c in n.d.items() if k2 != '']
            if not coefs or any(c % p for c in coefs):
                return None
            r = n.d.get('', 0) % p
            y = (n - r) / p
            if lb(y) < 0:
                return None
            return y, int(r)
        for L in (1, 2, 3):
            for p in (1, 2, 3):
                if h - 1 >= 0 and not isinstance(t[h - 1], str) and h + L <= len(t) and all(isinstance(c, str) for c in t[h:h + L]):
                    w0, n0 = t[h - 1][1], t[h - 1][2]
                    rg = regroup(n0, p)
                    if rg:
                        w = w0 * p; ctx = ''.join(t[h:h + L])
                        w2 = ctx_shift(s.T, w, ctx, s.q, 'L')
                        if w2 is not None:
                            y, r = rg
                            t[h - 1:h + L] = list(w0 * r) + list(ctx) + [['B', w2, y]]
                            s.h = h - 1 + len(w0) * r; s.macro += 1
                            return None
                if h + 1 < len(t) and not isinstance(t[h + 1], str) and h - L + 1 >= 0 and all(isinstance(c, str) for c in t[h - L + 1:h + 1]):
                    w0, n0 = t[h + 1][1], t[h + 1][2]
                    rg = regroup(n0, p)
                    if rg:
                        w = w0 * p; ctx = ''.join(t[h - L + 1:h + 1])
                        w2 = ctx_shift(s.T, w, ctx, s.q, 'R')
                        if w2 is not None:
                            y, r = rg
                            t[h - L + 1:h + 2] = [['B', w2, y]] + list(ctx) + list(w0 * r)
                            s.h = h + 1; s.macro += 1
                            return None
        x = t[h]
        if not isinstance(x, str):
            raise Fail('head on block')
        tr = s.T[(s.q, x)]
        if tr is None:
            return ('HALT', s.q)
        t[h] = tr[0]
        s.q = tr[2]
        d = tr[1]
        s.steps += 1
        nh = h + d
        while True:
            if nh < 0:
                t.insert(0, '0')
                s.h = 0
                return ('Lnew', s.q)
            if nh >= len(t):
                t.append('0')
                s.h = len(t) - 1
                s.rnew = getattr(s, 'rnew', 0) + 1
                return ('Rnew', s.q)
            y = t[nh]
            if isinstance(y, str):
                s.h = nh
                return None
            frm = 'L' if d == 1 else 'R'
            w, n = y[1], y[2]
            if n.isconst() and n.const() == 0:
                del t[nh]
                if d == -1:
                    nh -= 1
                continue
            r = copy_sim(s.T, w, s.q, frm)
            if r and r[0] != frm and r[1] == s.q:
                y[1] = r[2]
                s.macro += 1
                nh = nh + d
                continue
            # regroup w^n as (w^p)^y w^r when every symbolic coefficient of n is divisible by p
            done = False
            for p in (2, 3, 4, 6):
                coefs = [c for k2, c in n.d.items() if k2 != '']
                if coefs and all(c % p == 0 for c in coefs):
                    c0 = n.d.get('', 0)
                    r = c0 % p
                    y = (n - r) / p
                    if lb(y) < 0:
                        continue
                    ww = w * p
                    rr = copy_sim(s.T, ww, s.q, frm)
                    if rr and rr[0] != frm and rr[1] == s.q:
                        blk = ['B', ww, y]
                        t[nh:nh + 1] = ([blk] + list(w * int(r))) if frm == 'L' else (list(w * int(r)) + [blk])
                        if frm == 'R':
                            nh = nh + len(w) * int(r)
                        done = True
                        break
            if done:
                continue
            if lb(n) < 1:
                raise Fail('cannot peel: count %r may be 0 (q=%s from %s w=%s ctx=%s)' % (n, s.q, frm, w, ''.join(c if isinstance(c,str) else '|%s^%r|'%(c[1],c[2]) for c in t[max(0,nh-6):nh+8])))
            n2 = n - 1
            # peel ONE CELL (rotation): w^n = w[0] (w[1:] w[0])^(n-1) w[1:]  (from the left), mirror from the right
            far = t[nh + 1] if frm == 'L' and nh + 1 < len(t) else (t[nh - 1] if frm == 'R' and nh >= 1 else None)
            if far is not None and not isinstance(far, str) and lb(n2) < 1:
                # whole-copy peel (keeps alignment; avoids stranding literals next to another block)
                if frm == 'L':
                    t[nh:nh + 1] = list(w) + [['B', w, n2]]
                else:
                    t[nh:nh + 1] = [['B', w, n2]] + list(w)
                    nh = nh + len(w)
                continue
            if frm == 'L':
                t[nh:nh + 1] = [w[0], ['B', w[1:] + w[0], n2]] + list(w[1:])
                bi = nh + 1
                # re-absorb literal copies on the far (right) side
                wr = t[bi][1]
                while bi + len(wr) < len(t) + 1 and all(isinstance(c, str) for c in t[bi + 1:bi + 1 + len(wr)]) and ''.join(t[bi + 1:bi + 1 + len(wr)]) == wr:
                    del t[bi + 1:bi + 1 + len(wr)]
                    t[bi][2] = t[bi][2] + 1
            else:
                t[nh:nh + 1] = list(w[:-1]) + [['B', w[-1] + w[:-1], n2], w[-1]]
                bi = nh + len(w) - 1
                wr = t[bi][1]
                while bi - len(wr) >= 0 and all(isinstance(c, str) for c in t[bi - len(wr):bi]) and ''.join(t[bi - len(wr):bi]) == wr:
                    del t[bi - len(wr):bi]
                    bi -= len(wr)
                    t[bi][2] = t[bi][2] + 1
                nh = bi + 1
            continue

    def run_pred(s, pred, maxsteps=10 ** 6):
        for _ in range(maxsteps):
            ev = s.step()
            if ev and ev[0] == 'HALT':
                return ev
            if pred(s):
                return ('PRED',)
        raise Fail('maxsteps')

    def run(s, stop, maxsteps=10 ** 6):
        for _ in range(maxsteps):
            ev = s.step()
            if ev and (ev[0] == 'HALT' or stop(ev, s)):
                return ev
        raise Fail('maxsteps')


def tape_digits(digs):
    """original orientation K-config: [D on new cell] 0 0 [1 (01)^d]... ; digs: int, Lin, or ('Z', Lin) = n digits of value 1"""
    items = ['0', '0', '0']
    for e in digs:
        if isinstance(e, tuple):
            items.append(['B', '101', e[1]])
        else:
            items.append('1')
            if isinstance(e, int):
                items += list('01' * e)
            else:
                items.append(['B', '01', e])
    return items


def decode(t, h):
    """tape after a Lnew D event (head at index h = new cell). expects exactly 0 0 then digits; else None."""
    st = []
    for x in t[h + 1:]:
        if isinstance(x, str):
            st.append(x)
        else:
            if x[2].isconst():
                st.extend(x[1] * int(x[2].const()))
            else:
                st.append(('blk', x[1], x[2]))
    while st and st[-1] == '0':
        st.pop()
    z = 0
    while z < len(st) and st[z] == '0':
        z += 1
    if z != 2:
        return None
    st = st[2:]
    digs = []
    cur = None
    pos = 0

    def rot(b):
        _, w, n = b
        return [w[0], ('blk', w[1:] + w[0], n - 1)] + list(w[1:])

    while pos < len(st):
        x = st[pos]
        if isinstance(x, tuple):
            w = x[1]
            if w == '01' and cur is not None:
                cur = cur + x[2]
                pos += 1
                continue
            if w == '101':
                if cur is not None:
                    digs.append(cur)
                if lb(x[2]) < 1:
                    raise Fail('101 block maybe empty')
                digs.append(('Z', x[2] - 1))
                cur = Lin.c(1)
                pos += 1
                continue
            if lb(x[2]) < 1:
                raise Fail('rot of maybe-empty block')
            st[pos:pos + 1] = rot(x)
            continue
        if x == '1':
            if cur is not None:
                digs.append(cur)
            cur = Lin.c(0)
            pos += 1
            continue
        if cur is None:
            return None
        nxt = st[pos + 1] if pos + 1 < len(st) else None
        if nxt == '1':
            cur = cur + 1
            pos += 2
            continue
        if isinstance(nxt, tuple):
            if lb(nxt[2]) < 1:
                raise Fail('rot of maybe-empty block')
            st[pos + 1:pos + 2] = rot(nxt)
            continue
        return None
    if cur is not None:
        digs.append(cur)
    out = []
    for d in digs:
        if isinstance(d, tuple):
            if d[1].isconst():
                out += [Lin.c(1)] * int(d[1].const())
            else:
                out.append(d)
        else:
            out.append(d)
    return out


def next_K(digs, maxsteps=10 ** 6):
    """run from K-config digs to the next p1 K-event (D moves onto a new left cell, then 0 0 1...).
    Other D-left events must be p2-shaped (cell right of the head is 1), else Fail."""
    s = Sim(tape_digits(digs), 0, 'D')
    while True:
        ev = s.run(lambda e, S: e[0] == 'Lnew' and e[1] == 'D', maxsteps)
        if ev[0] == 'HALT':
            return 'HALT', s
        d = decode(s.t, s.h)
        if d is not None:
            return d, s
        if s.t[1] != '1':
            raise Fail('unclassified D-left event')


def V(name, lbv):
    LB[name] = lbv
    return Lin({name: 1})


def fl(v):
    out = []
    for e in v:
        if isinstance(e, tuple) and e[1].isconst():
            out += [Lin.c(1)] * int(e[1].const())
        else:
            out.append(e if isinstance(e, (Lin, tuple)) else Lin.c(e))
    return out


def same(a, b):
    a = fl(a)
    b = fl(b)
    return len(a) == len(b) and all((isinstance(x, tuple) == isinstance(y, tuple)) and
                                    ((x[1] == y[1]) if isinstance(x, tuple) else x == y) for x, y in zip(a, b))


def show(d):
    if isinstance(d, str):
        return d
    return '[' + ', '.join(('1^{%r}' % e[1]) if isinstance(e, tuple) else repr(e) for e in d) + ']'
