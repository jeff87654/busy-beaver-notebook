"""Planner mirroring busycoq's `execute` on tapes with symbolic runs.

Tape model (mirrors Coq):
  config = (q, L, R, mode); L and R are token lists, nearest-to-head first, ending in a terminator.
  mode '>' : head cell is first cell of R   (Coq: L {{q}}> R)
  mode '<' : head cell is first cell of L   (Coq: L <{{q}} R)
  tokens: 0/1 concrete; ('run', block, cnt) with block a tuple in STREAM order (nearest first),
          cnt a linear form: tuple of sorted (var, coeff) with no constant part (constants are peeled,
          as Coq's simpl does for S-counts; finish_norm pulls S out of sums).
  terminators: ('BLANK',) = const 0 ; ('VAR', name) = unknown stream (reading it is an error)
Coq's simpl_tape absorbs trailing zeros into const 0 (rewrite <- const_unfold).
"""

TMS = "1RB1LD_1RC0RF_0LA0RA_0LA0LE_1LA0LG_0LA---_1RD1LG"
QS = 'ABCDEFG'
T = {}
for qi, ch in enumerate(TMS.split('_')):
    for s in (0, 1):
        e = ch[3 * s:3 * s + 3]
        T[(QS[qi], s)] = None if e == '---' else (int(e[0]), 1 if e[1] == 'R' else -1, e[2])

BLANK = ('BLANK',)


def V(n):
    return ('VAR', n)


def lin(d):
    return tuple(sorted((k, v) for k, v in d.items() if v))


def lin_add(a, b, cb=1):
    d = dict(a)
    for k, v in b:
        d[k] = d.get(k, 0) + cb * v
    return lin(d)


def mkrun(block, var_coeffs, const=0):
    """Tokens for block^(linear + const): const concrete blocks first (peeled), then the run."""
    toks = []
    for _ in range(const):
        toks.extend(block)
    c = lin(var_coeffs) if isinstance(var_coeffs, dict) else var_coeffs
    if c:
        toks.append(('run', tuple(block), c))
    return toks


def cnt_str(c):
    if not c:
        return '0'
    return '+'.join(('%s' % k) if v == 1 else ('%d%s' % (v, k)) for k, v in c)


def is_term(t):
    return isinstance(t, tuple) and t[0] in ('BLANK', 'VAR')


def is_run(t):
    return isinstance(t, tuple) and t[0] == 'run'


def norm_side(side):
    side = list(side)
    if side[-1] == BLANK:
        while len(side) >= 2 and side[-2] == 0:
            del side[-2]
    return side


class Stuck(Exception):
    pass


def head(cfg):
    q, L, R, mode = cfg
    side = R if mode == '>' else L
    t = side[0]
    if t == BLANK:
        return 0
    if isinstance(t, int):
        return t
    raise Stuck(t)


def step(cfg):
    q, L, R, mode = cfg
    s = head(cfg)
    tr = T[(q, s)]
    if tr is None:
        raise RuntimeError('HALT reached at %r' % (cfg,))
    w, d, q2 = tr
    if mode == '>':
        rest = R if R[0] == BLANK else R[1:]
        if d == 1:
            return (q2, norm_side([w] + L), norm_side(rest), '>')
        return (q2, L, norm_side([w] + rest), '<')
    rest = L if L[0] == BLANK else L[1:]
    if d == -1:
        return (q2, norm_side(rest), norm_side([w] + R), '<')
    return (q2, norm_side([w] + rest), R, '>')


# ---------------------------------------------------------------- crossing lemmas
LEMMAS = {}


def derive_crossing(q, direction, xs, behind):
    nb = len(behind)
    if direction == '>':
        tape = list(reversed(behind)) + list(xs)
        pos = nb
        exit_pos = nb + len(xs)
    else:
        tape = list(reversed(xs)) + list(behind)
        pos = len(xs) - 1
        exit_pos = -1
    st = q
    minpos, maxpos = pos, pos
    for _ in range(2000):
        if pos == exit_pos:
            break
        if not (0 <= pos < len(tape)):
            return None, 'left known region at pos %d' % pos
        tr = T[(st, tape[pos])]
        if tr is None:
            return None, 'halt'
        w, d, st = tr
        tape[pos] = w
        pos += d
        minpos, maxpos = min(minpos, pos), max(maxpos, pos)
    else:
        return None, 'loop'
    if st != q:
        return None, 'exit state %s != %s' % (st, q)
    if direction == '>':
        depth = nb - minpos if minpos < nb else 0
        ctx_before = list(behind[:depth])
        after_behind = list(reversed(tape[:nb]))
        ctx_after = after_behind[:depth]
        ys = list(reversed(tape[nb:]))
    else:
        nx = len(xs)
        depth = (maxpos - (nx - 1)) if maxpos > nx - 1 else 0
        ctx_before = list(behind[:depth])
        after_behind = tape[nx:]
        ctx_after = after_behind[:depth]
        ys = tape[:nx]
    if ctx_after != ctx_before:
        return None, 'context changed %r -> %r' % (ctx_before, ctx_after)
    if (ys + ctx_before)[:depth] != ctx_before:
        return None, 'not inductive: ys=%r ctx=%r' % (ys, ctx_before)
    return dict(q=q, dir=direction, xs=tuple(xs), ys=tuple(ys), ctx=tuple(ctx_before)), None


def lemma_name(lm):
    d = 'R' if lm['dir'] == '>' else 'L'
    s = 'cross_%s%s_%s_%s' % (lm['q'], d, ''.join(map(str, lm['xs'])), ''.join(map(str, lm['ys'])))
    if lm['ctx']:
        s += '_c' + ''.join(map(str, lm['ctx']))
    return s


def concrete_prefix(side):
    out = []
    for t in side:
        if isinstance(t, int):
            out.append(t)
        elif t == BLANK:
            out.extend([0] * 6)
            break
        else:
            break
    return out


def apply_crossing(cfg):
    q, L, R, mode = cfg
    if mode == '>':
        run = R[0]
        behind = concrete_prefix(L)
    else:
        run = L[0]
        behind = concrete_prefix(R)
    if not is_run(run):
        raise RuntimeError('stuck on non-run %r at %s' % (run, show(cfg)))
    _, xs, cnt = run
    lm, why = derive_crossing(q, mode, xs, behind)
    if lm is None:
        # try one align step on the run under the head: (x::xs)^^n *> x >> ys = x >> (xs++[x])^^n *> ys
        side = R if mode == '>' else L
        if len(side) > 1 and isinstance(side[1], int) and side[1] == xs[0]:
            x0 = xs[0]
            new = [x0, ('run', tuple(xs[1:]) + (x0,), cnt)] + side[2:]
            name = ('ALIGN', x0, tuple(xs[1:]), cnt)
            if mode == '>':
                return (q, L, norm_side(new), '>'), name
            return (q, norm_side(new), R, '<'), name
        raise RuntimeError('no crossing at %s: %s' % (show(cfg), why))
    name = lemma_name(lm)
    LEMMAS[name] = lm
    if mode == '>':
        return (q, norm_side([('run', lm['ys'], cnt)] + L), R[1:], '>'), name
    return (q, L[1:], norm_side([('run', lm['ys'], cnt)] + R), '<'), name


# ---------------------------------------------------------------- display
def tok_str(t, left):
    if isinstance(t, int):
        return str(t)
    if t == BLANK:
        return '0^inf'
    if t[0] == 'VAR':
        return t[1]
    blk = t[1]
    if left:
        blk = tuple(reversed(blk))
    return '(%s)^{%s}' % (''.join(map(str, blk)), cnt_str(t[2]))


def show(cfg):
    q, L, R, mode = cfg
    ls = ' '.join(tok_str(t, True) for t in reversed(L))
    rs = ' '.join(tok_str(t, False) for t in R)
    if mode == '>':
        return '%s  %s> %s' % (ls, q, rs)
    return '%s <%s  %s' % (ls, q, rs)


# ---------------------------------------------------------------- canonical (align) normal form
def expand_side(side):
    side = list(side)
    changed = True
    while changed:
        changed = False
        for i, t in enumerate(side):
            if is_run(t) and i + 1 < len(side) and isinstance(side[i + 1], int) and side[i + 1] == t[1][0]:
                x = side[i + 1]
                blk = t[1][1:] + (x,)
                side = side[:i] + [x, ('run', blk, t[2])] + side[i + 2:]
                changed = True
                break
            if is_run(t) and i + 1 < len(side) and side[i + 1] == BLANK and t[1][0] == 0:
                blk = t[1][1:] + (0,)
                side = side[:i] + [0, ('run', blk, t[2])] + side[i + 1:]
                changed = True
                break
    return norm_side(side)


def triple(cfg):
    q, L, R, mode = cfg
    side = R if mode == '>' else L
    t = side[0]
    if t == BLANK or isinstance(t, int):
        s = 0 if t == BLANK else t
        rest = side if t == BLANK else side[1:]
        if mode == '>':
            return (q, L, s, rest)
        return (q, rest, s, R)
    return (q, L, mode, R)


def canon(cfg):
    q, L, s, R = triple(cfg)
    return (q, tuple(expand_side(L)), s, tuple(expand_side(R)))


# ---------------------------------------------------------------- L0* matcher
def parse_group(toks, i, block):
    """concrete copies of block then at most one run of block. Returns (const, lin, new_i)."""
    c = 0
    n = len(block)
    while list(toks[i:i + n]) == list(block) and all(isinstance(t, int) for t in toks[i:i + n]):
        c += 1
        i += n
    ln = ()
    if i < len(toks) and is_run(toks[i]) and toks[i][1] == tuple(block):
        ln = toks[i][2]
        i += 1
    return c, ln, i


def match_L0s(cfg):
    """const 0 {{A}}> 0 >> 0 >> [1;0;0]^^j *> 1 >> 0 >> 1 >> 0 >> [1;1;0]^^k *> r ; returns (j, k, rest) or None"""
    q, L, s, R = triple(cfg)
    if q != 'A' or s != 0 or list(L) != [BLANK]:
        return None
    R = list(R)
    if R[:1] != [0]:
        return None
    jc, jl, i = parse_group(R, 1, (1, 0, 0))
    if R[i:i + 4] != [1, 0, 1, 0]:
        return None
    i += 4
    # K group: concrete cells, then a run that (after forward align steps) becomes (110)^n with a
    # concrete prefix consisting of whole (110) blocks.
    j2 = i
    while j2 < len(R) and isinstance(R[j2], int):
        j2 += 1
    aligns = []
    if j2 < len(R) and is_run(R[j2]):
        pre = list(R[i:j2])
        blk, cnt = R[j2][1], R[j2][2]
        k = j2 + 1
        while blk != (1, 1, 0) and k < len(R) and isinstance(R[k], int) and R[k] == blk[0]:
            aligns.append((blk[0], blk[1:], cnt))
            pre.append(blk[0])
            blk = blk[1:] + (blk[0],)
            k += 1
        if blk == (1, 1, 0) and len(pre) % 3 == 0 and pre == [1, 1, 0] * (len(pre) // 3):
            return (jc, jl), (len(pre) // 3, cnt), R[k:], aligns
    kc, kl, i2 = parse_group(R, i, (1, 1, 0))
    return (jc, jl), (kc, kl), R[i2:], []


def apply_L0s(cfg):
    (jc, jl), (kc, kl), rest, _ = match_L0s(cfg)
    # result count j + 2k
    nl = lin_add(jl, kl, 2)
    nc = jc + 2 * kc
    R = [0] + mkrun((1, 0, 0), nl, nc) + [1, 0, 1, 0] + list(rest)
    return ('A', [BLANK], norm_side([0] + R), '>')
