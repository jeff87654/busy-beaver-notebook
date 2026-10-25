"""Planner mirroring busycoq's `execute` on tapes with symbolic runs (generic TM).
Adapted from ../bb7_control_16582/coq_scratch/planner.py.

config = (q, L, R, mode); L, R token lists nearest-to-head first, ending in a terminator.
  mode '>' : head cell is first cell of R   (Coq: L {{q}}> R)
  mode '<' : head cell is first cell of L   (Coq: L <{{q}} R)
tokens: 0/1; ('run', block, cnt) block in STREAM order (nearest head first), cnt = linear form
        (tuple of sorted (var, coeff)), no constant part (constants are peeled into concrete cells);
terminators: ('BLANK',) = const 0 ; ('VAR', name) = unknown stream (reading it is an error).
"""
import sys

QS = 'ABCDEFGH'
T = {}


def set_tm(tms):
    T.clear()
    for qi, ch in enumerate(tms.split('_')):
        for s in (0, 1):
            e = ch[3 * s:3 * s + 3]
            T[(QS[qi], s)] = None if e == '---' else (int(e[0]), 1 if e[1] == 'R' else -1, e[2])


MAIN = "1RB1RA_0RC0RA_0LD1RC_1RE1LE_1LF0LG_1LB0RD_0LH1LF_1RF---"
set_tm(MAIN)
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


class Halted(Exception):
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
        raise Halted('HALT reached at %s' % show(cfg))
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
    """Simulate one copy of block xs (stream order) entered in state q; must exit on the far side in q.
    behind = concrete cells behind the head (stream order away from the block), may be read but must be restored."""
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
    for _ in range(5000):
        if pos == exit_pos:
            break
        if not (0 <= pos < len(tape)):
            return None, 'left known region at pos %d (state %s)' % (pos, st)
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


def derive_crossing2(q, direction, xs, behind):
    """mode 2: the cells nearest the head (ctx, depth d) stay put and the converted block is inserted BEHIND them:
    '>' : (ctx ++ l) {{q}}> xs^^n *> r -->* (ctx ++ ys^^n *> l) {{q}}> r
    '<' : l <{{q}} xs^^n(in left stream) ... mirrored."""
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
    for _ in range(5000):
        if pos == exit_pos:
            break
        if not (0 <= pos < len(tape)):
            return None, 'left known region at pos %d (state %s)' % (pos, st)
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
    nx = len(xs)
    if direction == '>':
        depth = nb - minpos if minpos < nb else 0
        new_beh = list(reversed(tape[:exit_pos]))   # nearest first, length nb+nx
    else:
        depth = (maxpos - (nx - 1)) if maxpos > nx - 1 else 0
        new_beh = list(tape)                         # nearest first, length nx+nb
    for d in range(depth, nb + 1):
        if new_beh[:d] == behind[:d] and new_beh[d + nx:] == behind[d:]:
            ys = new_beh[d:d + nx]
            return dict(q=q, dir=direction, xs=tuple(xs), ys=tuple(ys), ctx=tuple(behind[:d]), mode=2), None
    return None, 'mode2: no consistent context'


def lemma_name(lm):
    d = 'R' if lm['dir'] == '>' else 'L'
    s = ('cx_' if lm.get('mode') == 2 else 'cr_') + '%s%s_%s_%s' % (lm['q'], d, ''.join(map(str, lm['xs'])), ''.join(map(str, lm['ys'])))
    if lm['ctx']:
        s += '_c' + ''.join(map(str, lm['ctx']))
    return s


def concrete_prefix(side):
    out = []
    for t in side:
        if isinstance(t, int):
            out.append(t)
        elif t == BLANK:
            out.extend([0] * 12)
            break
        else:
            break
    return out


def try_crossing(cfg):
    q, L, R, mode = cfg
    run = R[0] if mode == '>' else L[0]
    behind = concrete_prefix(L if mode == '>' else R)
    if not is_run(run):
        return None, 'not a run'
    _, xs, cnt = run
    lm, why = derive_crossing(q, mode, xs, behind)
    if lm is None:
        lm, why2 = derive_crossing2(q, mode, xs, behind)
        if lm is None:
            return None, why + ' | ' + why2
    name = lemma_name(lm)
    LEMMAS[name] = lm
    if lm.get('mode') == 2:
        d = len(lm['ctx'])
        back = L if mode == '>' else R
        if list(back[:d]) != list(lm['ctx']):
            return None, 'mode2 ctx not at front of stream'
        newback = norm_side(list(back[:d]) + [('run', lm['ys'], cnt)] + list(back[d:]))
        if mode == '>':
            return ((q, newback, R[1:], '>'), name), None
        return ((q, L[1:], newback, '<'), name), None
    if mode == '>':
        return ((q, norm_side([('run', lm['ys'], cnt)] + L), R[1:], '>'), name), None
    return ((q, L[1:], norm_side([('run', lm['ys'], cnt)] + R), '<'), name), None


def try_align(cfg):
    """(x::xs)^^n *> x >> ys = x >> (xs++[x])^^n *> ys  on the side under the head."""
    q, L, R, mode = cfg
    side = R if mode == '>' else L
    run = side[0]
    if not is_run(run):
        return None
    xs = run[1]
    if len(side) > 1 and isinstance(side[1], int) and side[1] == xs[0]:
        x0 = xs[0]
        new = [x0, ('run', tuple(xs[1:]) + (x0,), run[2])] + side[2:]
        name = ('ALIGN', x0, tuple(xs[1:]), run[2])
        if mode == '>':
            return (q, L, norm_side(new), '>'), name
        return (q, norm_side(new), R, '<'), name
    if len(side) > 1 and side[1] == BLANK and xs[0] == 0:
        new = [0, ('run', tuple(xs[1:]) + (0,), run[2]), BLANK]
        name = ('ALIGNC', 0, tuple(xs[1:]), run[2])
        if mode == '>':
            return (q, L, norm_side(new), '>'), name
        return (q, norm_side(new), R, '<'), name
    return None


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


# ---------------------------------------------------------------- canonical form (for target comparison)
def expand_side(side):
    """push concrete symbols in front of runs (align normal form), merge adjacent equal runs"""
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
            if is_run(t) and i + 1 < len(side) and is_run(side[i + 1]) and side[i + 1][1] == t[1]:
                side = side[:i] + [('run', t[1], lin_add(t[2], side[i + 1][2]))] + side[i + 2:]
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


# ---------------------------------------------------------------- driver
def pieces(c):
    return sum(v for _, v in c)


def drive(name, cfg, target=None, matchers=(), maxev=400, verbose=True, stop_at=None):
    """matchers: functions cfg -> None | (newcfg, script_fragment, description), tried at stuck points
    (or before every literal step if the function has attribute .anytime = True)."""
    if verbose:
        print('=====', name)
        print('  start :', show(cfg))
        if target:
            print('  target:', show(target))
    ct = canon(target) if target else None
    script = []
    n = 0
    total = 0
    for ev in range(maxev):
        while True:
            if ct is not None and canon(cfg) == ct:
                script.append(('end', n))
                if verbose:
                    print('  reached target after %d more steps (%d total literal steps)' % (n, total))
                return script, cfg
            done = False
            for m in matchers:
                if getattr(m, 'anytime', False):
                    r = m(cfg)
                    if r:
                        cfg2, frag, desc = r
                        script.append(('steps', n)); script.append(('lemma', frag))
                        if verbose:
                            print('  [%3d steps] %s at: %s' % (n, desc, show(cfg)))
                            print('       -> %s' % show(cfg2))
                        cfg = cfg2; n = 0; done = True
                        break
            if done:
                continue
            try:
                head(cfg)
            except Stuck:
                break
            cfg = step(cfg)
            n += 1; total += 1
            if n > 200000:
                raise RuntimeError('literal step limit')
        # stuck at a run
        if stop_at and stop_at(cfg):
            script.append(('steps', n))
            if verbose:
                print('  [%3d steps] STOP: %s' % (n, show(cfg)))
            return script, cfg
        done = False
        for m in matchers:
            if getattr(m, 'anytime', False):
                continue
            r = m(cfg)
            if r:
                cfg2, frag, desc = r
                script.append(('steps', n)); script.append(('lemma', frag))
                if verbose:
                    print('  [%3d steps] %s at: %s' % (n, desc, show(cfg)))
                    print('       -> %s' % show(cfg2))
                cfg = cfg2; n = 0; done = True
                break
        if done:
            continue
        r, why = try_crossing(cfg)
        if r:
            cfg2, lname = r
            q, L, R, mode = cfg
            run = R[0] if mode == '>' else L[0]
            script.append(('steps', n)); script.append(('cross', lname, pieces(run[2])))
            if verbose:
                print('  [%3d steps] follow %s (x%d) at: %s' % (n, lname, pieces(run[2]), show(cfg)))
            cfg = cfg2; n = 0
            continue
        a = try_align(cfg)
        if a:
            cfg2, aname = a
            script.append(('steps', n)); script.append(('align', aname))
            if verbose:
                print('  [%3d steps] align %r at: %s  (crossing failed: %s)' % (n, aname, show(cfg), why))
            cfg = cfg2; n = 0
            continue
        if verbose:
            print('  [%3d steps] STUCK (%s): %s' % (n, why, show(cfg)))
        script.append(('stuck', n))
        return script, cfg
    raise RuntimeError('maxev')


# ---------------------------------------------------------------- tape words
LET = {'x': (1,), 'a': (1, 0), 'b': (1, 0, 0), 'c': (1, 0, 0, 0)}


def bits(word):
    out = []
    for ch in word:
        out.extend(LET[ch])
    return tuple(out)
