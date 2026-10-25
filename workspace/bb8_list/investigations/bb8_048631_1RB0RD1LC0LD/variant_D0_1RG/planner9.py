"""planner9: symbolic executor mirroring busycoq's [step] on tapes with symbolic runs whose counts are
AFFINE forms (constant + sum coef*var), for 1RB0RD_1LC0LD_1LA1RC_0LB0RE_1LF1RA_1LG---_0LH1LE_0LA0LB.

Derived from ../neighbors_family_tools/planner8.py.  Differences:
  * counts are affine (constant part allowed); the Coq text of a count is canonical:
        vars part "3 * x + y" (sorted), then " + k" if k > 0;  pure constants k > SMALL are "cnt k";
        pure constants k <= SMALL are expanded into concrete cells (Coq's simpl unfolds them too).
  * the Coq side uses step' (simpl_tape without lpow_add / lpow_shift'), Nat.mul is [simpl never],
    and cnt is [simpl never]; hence Coq never changes a count term by itself and the planner knows
    every count's exact syntax.
  * peeling one copy off a run whose constant part is >= 1 is an explicit rewrite (lpow_peel_add /
    lpow_peel_add1 / lpow_peel_cnt).
  * absorbing concrete copies into an adjacent run is an explicit rewrite (absorb3 / absorbr3).

config = (q, L, R, mode); L, R token lists nearest-to-head first, ending in a terminator.
  mode '>' : head cell is first cell of R   (Coq: L {{q}}> R)
  mode '<' : head cell is first cell of L   (Coq: L <{{q}} R)
tokens: 0/1; ('run', block, cnt) block in STREAM order (nearest head first), cnt = (k, ((var, coef), ...));
terminators: ('BLANK',) = const 0 ; ('VAR', name).
"""
QS = 'ABCDEFGH'
T = {}
SMALL = 1
BLANK = ('BLANK',)


def set_tm(tms):
    T.clear()
    for qi, ch in enumerate(tms.split('_')):
        for s in (0, 1):
            e = ch[3 * s:3 * s + 3]
            T[(QS[qi], s)] = None if e == '---' else (int(e[0]), 1 if e[1] == 'R' else -1, e[2])


import os
TM = os.environ.get("BB8TM", "1RB0RD_1LC0LD_1LA1RC_0LB0RE_1LF1RA_1LG---_0LH1LE_0LA0LB")
set_tm(TM)


def V(n):
    return ('VAR', n)


# ---------------------------------------------------------------- affine counts
def C(k=0, **vs):
    return (k, tuple(sorted((v, c) for v, c in vs.items() if c)))


def cadd(a, b, cb=1):
    d = dict(a[1])
    for v, c in b[1]:
        d[v] = d.get(v, 0) + cb * c
    return (a[0] + cb * b[0], tuple(sorted((v, c) for v, c in d.items() if c)))


def cconst(k):
    return (k, ())


def cscale(a, m):
    return (a[0] * m, tuple((v, c * m) for v, c in a[1]))


def cvarpart(a):
    return ' + '.join(v if c == 1 else '%d * %s' % (c, v) for v, c in a[1])


THR = 30   # constants above THR are written in binary as [kN k] (unary numerals make every step slow)


def kconst(k):
    return '%d' % k if k <= THR else 'kN %d' % k


def ccoq(a):
    k, vs = a
    assert k >= 0, a
    if vs:
        s = cvarpart(a)
        if k:
            s += ' + ' + kconst(k)
        return '(' + s + ')'
    return '(kN %d)' % k


def cstr(a):
    k, vs = a
    s = cvarpart(a)
    if not vs:
        return str(k)
    return s + ('+%d' % k if k else '')


def is_term(t):
    return isinstance(t, tuple) and t[0] in ('BLANK', 'VAR')


def is_run(t):
    return isinstance(t, tuple) and t[0] == 'run'


def mkrun(blk, cnt):
    """run token, expanded into cells when the count is a small pure constant."""
    blk = tuple(blk)
    k, vs = cnt
    if not vs:
        if k <= SMALL:
            return list(blk) * k
    return [('run', blk, cnt)]


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


def lemma_name(lm):
    d = 'R' if lm['dir'] == '>' else 'L'
    s = 'cr_%s%s_%s_%s' % (lm['q'], d, ''.join(map(str, lm['xs'])), ''.join(map(str, lm['ys'])))
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
        return None, why
    name = lemma_name(lm)
    LEMMAS[name] = lm
    newrun = ('run', lm['ys'], cnt)
    if mode == '>':
        return ((q, norm_side([newrun] + L), R[1:], '>'), name), None
    return ((q, L[1:], norm_side([newrun] + R), '<'), name), None


# ---------------------------------------------------------------- explicit rewrites (Coq text + planner effect)
def cl(t):
    return '[' + ';'.join(map(str, t)) + ']'


def peel(cfg):
    """peel one copy off the run under the head; returns (cfg, coq_text) or None."""
    q, L, R, mode = cfg
    side = R if mode == '>' else L
    t = side[0]
    if not is_run(t):
        return None
    _, blk, cnt = t
    k, vs = cnt
    if k < 1:
        return None
    rest = side[1:]
    newc = (k - 1, vs)
    if vs:
        txt = 'rewrite (lpow_peel_gen _ %s %s %s ltac:(kN_lia)).' % (cl(blk), ccoq(cnt), ccoq(newc))
        newside = list(blk) + [('run', blk, newc)] + rest
    else:
        if k - 1 <= SMALL:
            txt = 'rewrite (lpow_peel_gen _ %s %s %d ltac:(kN_lia)).' % (cl(blk), ccoq(cnt), k - 1)
            newside = list(blk) + list(blk) * (k - 1) + rest
        else:
            txt = 'rewrite (lpow_peel_gen _ %s %s %s ltac:(kN_lia)).' % (cl(blk), ccoq(cnt), ccoq(newc))
            newside = list(blk) + [('run', blk, newc)] + rest
    txt += ' simpl.'
    newside = norm_side(newside)
    if mode == '>':
        return (q, L, newside, '>'), txt
    return (q, newside, R, '<'), txt


def absorb_side(side, i, where):
    """side[i] is a run; absorb one concrete copy of its block that sits just BEFORE it in the stream
    (where='near': cells side[i-len:i]) or just AFTER it (where='far').  Returns (newside, coq_text)."""
    _, blk, cnt = side[i]
    n = len(blk)
    newc = cadd(cnt, cconst(1))
    assert n == 3
    if where == 'near':
        assert tuple(side[i - n:i]) == blk
        new = side[:i - n] + [('run', blk, newc)] + side[i + 1:]
        txt = 'rewrite (absorb3 %d %d %d %s %s _ ltac:(kN_lia)).' % (blk + (ccoq(cnt), ccoq(newc)))
    else:
        assert tuple(side[i + 1:i + 1 + n]) == blk
        new = side[:i] + [('run', blk, newc)] + side[i + 1 + n:]
        txt = 'rewrite (absorbr3 %d %d %d %s %s _ ltac:(kN_lia)).' % (blk + (ccoq(cnt), ccoq(newc)))
    return new, txt


def absorb_all(cfg):
    """absorb every concrete copy adjacent to a run (both sides of the head; never the head cell).
    Returns (cfg, [coq texts])."""
    q, L, R, mode = cfg
    texts = []

    def do(side, protect_first):
        side = list(side)
        changed = True
        while changed:
            changed = False
            for i, t in enumerate(side):
                if not is_run(t):
                    continue
                blk = t[1]
                n = len(blk)
                lo = 1 if protect_first else 0
                if i - n >= lo and all(isinstance(c, int) for c in side[i - n:i]) and tuple(side[i - n:i]) == blk:
                    side, txt = absorb_side(side, i, 'near')
                    texts.append(txt)
                    changed = True
                    break
                if all(isinstance(c, int) for c in side[i + 1:i + 1 + n]) and tuple(side[i + 1:i + 1 + n]) == blk:
                    side, txt = absorb_side(side, i, 'far')
                    texts.append(txt)
                    changed = True
                    break
        return side

    L2 = do(L, mode == '<')
    R2 = do(R, mode == '>')
    return (q, L2, R2, mode), texts


def count_runs(cfg, blk, cnt):
    q, L, R, mode = cfg
    return sum(1 for t in L + R if is_run(t) and t[1] == blk and t[2] == cnt)


def rotate_side(side, i):
    """rotate run side[i] by moving the cell just after it (stream order) in front of it:
       (x::xs)^^n *> x >> ys = x >> (xs ++ [x])^^n *> ys.  Returns (newside, coq) or None."""
    t = side[i]
    blk = t[1]
    if i + 1 < len(side) and isinstance(side[i + 1], int) and side[i + 1] == blk[0]:
        x0 = blk[0]
        new = side[:i] + [x0, ('run', tuple(blk[1:]) + (x0,), t[2])] + side[i + 2:]
        txt = 'rewrite (align_lpow %d %s _ %s). simpl app.' % (x0, cl(blk[1:]), ccoq(t[2]))
        return new, txt
    if i + 1 < len(side) and side[i + 1] == BLANK and blk[0] == 0:
        new = side[:i] + [0, ('run', tuple(blk[1:]) + (0,), t[2]), BLANK]
        txt = 'rewrite (align_lpow_const 0 %s _). simpl app.' % (cl(blk[1:]),)
        return new, txt
    return None


def realign(side, i, want):
    """rotate run side[i] until its block is `want` (a rotation of it).  Returns (newside, newi, texts) or None."""
    texts = []
    side = list(side)
    for _ in range(len(want)):
        if side[i][1] == want:
            return side, i, texts
        r = rotate_side(side, i)
        if r is None:
            return None
        side, txt = r
        texts.append(txt)
        i += 1
    return (side, i, texts) if side[i][1] == want else None


def align(cfg):
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
        txt = 'rewrite (align_lpow %d %s _ %s). simpl app.' % (x0, cl(xs[1:]), ccoq(run[2]))
    elif len(side) > 1 and side[1] == BLANK and xs[0] == 0:
        new = [0, ('run', tuple(xs[1:]) + (0,), run[2]), BLANK]
        txt = 'rewrite (align_lpow_const 0 %s _). simpl app.' % (cl(xs[1:]),)
    else:
        return None
    if mode == '>':
        return (q, L, norm_side(new), '>'), txt
    return (q, norm_side(new), R, '<'), txt


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
    return '(%s)^{%s}' % (''.join(map(str, blk)), cstr(t[2]))


def compress_cells(strs):
    out = []
    i = 0
    while i < len(strs):
        if strs[i] in ('0', '1'):
            j = i
            while j < len(strs) and strs[j] in ('0', '1'):
                j += 1
            out.append(''.join(strs[i:j]))
            i = j
        else:
            out.append(strs[i])
            i += 1
    return ' '.join(out)


def show(cfg):
    q, L, R, mode = cfg
    ls = compress_cells([tok_str(t, True) for t in reversed(L)])
    rs = compress_cells([tok_str(t, False) for t in R])
    if mode == '>':
        return '%s  %s> %s' % (ls, q, rs)
    return '%s <%s  %s' % (ls, q, rs)


# ---------------------------------------------------------------- Coq text of configurations
def side_coq(side):
    out = []
    for t in side:
        if isinstance(t, int):
            out.append('%d >> ' % t)
        elif t == BLANK:
            out.append('const 0')
        elif t[0] == 'VAR':
            out.append(t[1])
        else:
            out.append('%s^^%s *> ' % (cl(t[1]), ccoq(t[2])))
    return ''.join(out)


def paren(s):
    return s if s == 'const 0' or s.isidentifier() else '(' + s + ')'


def cfg_coq(cfg):
    q, L, R, mode = cfg
    if mode == '>':
        return '%s {{%s}}> %s' % (paren(side_coq(L)), q, paren(side_coq(R)))
    return '%s <{{%s}} %s' % (paren(side_coq(L)), q, paren(side_coq(R)))


def vars_of(cfg):
    q, L, R, mode = cfg
    vs = []
    for t in L + R:
        if is_run(t):
            for v, _ in t[2][1]:
                if v not in vs:
                    vs.append(v)
        elif isinstance(t, tuple) and t[0] == 'VAR' and t[1] not in vs:
            vs.append(t[1])
    return vs


# ---------------------------------------------------------------- driver
def drive(name, cfg, target=None, matchers=(), maxev=3000, verbose=True, maxlit=400000, prefer_peel=()):
    """Run until the configuration equals target (exact token equality).
    matchers: functions cfg -> None | (newcfg, [coq texts], description); tried before literal steps
    when their attribute .anytime is True, otherwise only at stuck points (before crossing)."""
    if verbose:
        print('=====', name)
        print('  start :', show(cfg))
        if target:
            print('  target:', show(target))
    script = []
    n = 0
    total = 0
    flags = []

    def flush():
        nonlocal n, flags
        if n:
            script.append(('lits', list(flags)))
        n = 0
        flags = []

    for ev in range(maxev):
        while True:
            if callable(target):
                if target(cfg):
                    flush()
                    cfgA, texts = absorb_all(cfg)
                    for t in texts:
                        script.append(('coq', t))
                    script.append(('stop',))
                    return script, cfgA
            elif target is not None:
                cfgA, texts = absorb_all(cfg) if cfg != target else (cfg, [])
                if cfgA == target:
                    flush()
                    for t in texts:
                        script.append(('coq', t))
                    script.append(('end',))
                    cfg = cfgA
                    if verbose:
                        print('  reached target (%d total literal steps)' % total)
                    return script, cfg
            done = False
            for m in matchers:
                if getattr(m, 'anytime', False):
                    r = m(cfg)
                    if r:
                        cfg2, frags, desc = r
                        flush()
                        for f in frags:
                            script.append(('coq', f))
                        if verbose:
                            print('  %s at: %s' % (desc, show(cfg)[:400]))
                        cfg = cfg2
                        done = True
                        break
            if done:
                continue
            try:
                head(cfg)
            except Stuck:
                break
            q_, L_, R_, m_ = cfg
            near_end = BLANK in L_[:2] or BLANK in R_[:2]
            cfg = step(cfg)
            q_, L_, R_, m_ = cfg
            near_end = near_end or BLANK in L_[:2] or BLANK in R_[:2]
            flags.append(near_end)
            n += 1
            total += 1
            if total > maxlit:
                raise RuntimeError('literal step limit')
        # stuck at a run
        done = False
        for m in matchers:
            if getattr(m, 'anytime', False):
                continue
            r = m(cfg)
            if r:
                cfg2, frags, desc = r
                flush()
                for f in frags:
                    script.append(('coq', f))
                if verbose:
                    print('  %s at: %s' % (desc, show(cfg)[:400]))
                cfg = cfg2
                done = True
                break
        if done:
            continue
        r, why = try_crossing(cfg)
        if r:
            cfg2, lname = r
            flush()
            script.append(('coq', 'follow %s.' % lname))
            if verbose:
                print('  follow %s at: %s' % (lname, show(cfg)[:300]))
            cfg = cfg2
            continue
        p = peel(cfg)
        if p:
            cfg2, txt = p
            flush()
            script.append(('coq', txt))
            if verbose:
                print('  peel (%s) at: %s' % (why, show(cfg)[:300]))
            cfg = cfg2
            continue
        a = align(cfg)
        if a:
            cfg2, txt = a
            flush()
            script.append(('coq', txt))
            if verbose:
                print('  align (crossing failed: %s) at: %s' % (why, show(cfg)[:300]))
            cfg = cfg2
            continue
        flush()
        if verbose:
            print('  STUCK (%s): %s' % (why, show(cfg)))
        script.append(('stuck',))
        return script, cfg
    raise RuntimeError('maxev')


def script_to_coq(script, plus):
    out = []
    first = True
    for op in script:
        if op[0] == 'lits':
            fl = list(op[1])
            if first and plus:
                out.append("step1c'." if fl[0] else "step1'.")
                fl = fl[1:]
            first = False
            i = 0
            while i < len(fl):
                if fl[i]:
                    out.append("stepc'.")
                    i += 1
                    continue
                j = i
                while j < len(fl) and not fl[j]:
                    j += 1
                out.append("do %d step'." % (j - i) if j - i > 1 else "step'.")
                i = j
            continue
        assert not (first and plus), 'a -->+ lemma must start with a literal step'
        first = False
        if op[0] == 'coq':
            out.append(op[1])
        elif op[0] == 'end':
            out.append('finish_eq.')
        elif op[0] == 'stop':
            pass
        else:
            raise RuntimeError('stuck: %r' % (op,))
    return out


def crossing_lemma(name, lm):
    q, d, xs, ys, ctx = lm['q'], lm['dir'], lm['xs'], lm['ys'], lm['ctx']
    ctxs = ''.join('%d >> ' % c for c in ctx)
    if d == '>':
        stmt = 'forall n l r, %sl {{%s}}> %s^^n *> r -->* %s^^n *> %sl {{%s}}> r' % (ctxs, q, cl(xs), cl(ys), ctxs, q)
    else:
        stmt = 'forall n l r, %s^^n *> l <{{%s}} %sr -->* l <{{%s}} %s^^n *> %sr' % (cl(xs), q, ctxs, q, cl(ys), ctxs)
    return ('Lemma %s : %s.\nProof. induction n; intros. - finish. - execute. follow IHn. finish_norm. Qed.\n'
            % (name, stmt))


def lemma_text(name, start, tgt, script, rel, extra_vars=()):
    vs = vars_of(start)
    for v in vars_of(tgt) + list(extra_vars):
        if v not in vs:
            vs.append(v)
    head_ = 'forall %s, ' % ' '.join(vs) if vs else ''
    stmt = '%s%s %s %s' % (head_, cfg_coq(start), rel, cfg_coq(tgt))
    tac = script_to_coq(script, rel == '-->+')
    body = 'Lemma %s : %s.\nProof.\n  intros.\n' % (name, stmt)
    line = '  '
    for t in tac:
        if len(line) + len(t) > 110:
            body += line.rstrip() + '\n'
            line = '  '
        line += t + ' '
    body += line.rstrip() + '\nQed.\n'
    return body


# ---------------------------------------------------------------- string-level comparison
def flat_side(side, env):
    out = []
    for t in side:
        if isinstance(t, int):
            out.append(str(t))
        elif t == BLANK:
            break
        elif t[0] == 'VAR':
            out.append('<%s>' % t[1])
            break
        else:
            k, vs = t[2]
            n = k + sum(c * env[v] for v, c in vs)
            out.append(''.join(map(str, t[1])) * n)
    s = ''.join(out)
    return s.rstrip('0') if side and side[-1] == BLANK else s


def same_string(c1, c2, trials=((3, 5, 7, 2), (11, 4, 9, 6), (6, 13, 2, 8))):
    """string equality of two symbolic configurations, tested at a few concrete substitutions."""
    if c1[0] != c2[0] or c1[3] != c2[3]:
        return False
    names = sorted(set(vars_of(c1)) | set(vars_of(c2)))
    for tr in trials:
        env = {v: tr[i % len(tr)] + 3 * i for i, v in enumerate(names)}
        if flat_side(c1[1], env) != flat_side(c2[1], env) or flat_side(c1[2], env) != flat_side(c2[2], env):
            return False
    return True


def drive_until_string2(name, cfg, target, matchers=(), maxev=20000, maxlit=400000):
    """stop at the first configuration string-equal to target; returns (script, cfg) with all adjacent
    concrete copies absorbed into runs (the absorbing rewrites are part of the script)."""
    def pred(c):
        return c[0] == target[0] and c[3] == target[3] and same_string(c, target)
    script, c = drive(name, cfg, pred, matchers=matchers, maxev=maxev, verbose=False, maxlit=maxlit)
    if not script or script[-1][0] != 'stop':
        return None, c
    return script, c


def drive_until_string(name, cfg, target, matchers=(), maxev=20000, maxlit=400000):
    """like drive, but stops at the first configuration string-equal to target (checked at E events and
    whenever the state/mode match).  Returns (script, cfg)."""
    def m_stop(c):
        if c[0] == target[0] and c[3] == target[3] and same_string(c, target):
            raise _Found(c)
        return None
    m_stop.anytime = True
    try:
        drive(name, cfg, None, matchers=[m_stop] + list(matchers), maxev=maxev, verbose=False, maxlit=maxlit)
    except _Found as f:
        return f.cfg
    return None


class _Found(Exception):
    def __init__(self, cfg):
        self.cfg = cfg


# ---------------------------------------------------------------- templates (families)
def make_template(cfg, names):
    """names: dict planner-var -> family-var.  Every run whose count involves planner var v becomes a run with
    count exactly family var names[v] (offset 0).  Returns (template, mapping) where mapping[famvar] = the
    affine count in cfg."""
    mapping = {}

    def conv(side):
        out = []
        for t in side:
            if is_run(t) and t[2][1]:
                vs = [v for v, _ in t[2][1]]
                assert len(vs) == 1, t
                fv = names[vs[0]]
                assert fv not in mapping or mapping[fv] == t[2], (fv, mapping.get(fv), t[2])
                mapping[fv] = t[2]
                out.append(('run', t[1], C(0, **{fv: 1})))
            else:
                out.append(t)
        return out
    q, L, R, mode = cfg
    return (q, conv(L), conv(R), mode), mapping


def instantiate(tpl, env):
    """env: family var -> affine count.  Substitutes and re-expands small constants."""
    def sub(cnt):
        k, vs = cnt
        out = cconst(k)
        for v, c in vs:
            out = cadd(out, cscale(env[v], c))
        return out

    def conv(side):
        out = []
        for t in side:
            if is_run(t):
                out.extend(mkrun(t[1], sub(t[2])))
            else:
                out.append(t)
        return norm_side(out)
    q, L, R, mode = tpl
    return (q, conv(L), conv(R), mode)


# ---------------------------------------------------------------- normalizing one symbolic tape into another
def _cnt_at(cnt, env):
    k, vs = cnt
    return k + sum(c * env[v] for v, c in vs)


def _run_positions(side, env):
    """list of (index, start, count) for the runs of a side (start = number of cells before the run)."""
    pos = 0
    out = []
    for i, t in enumerate(side):
        if isinstance(t, int):
            pos += 1
        elif is_run(t):
            n = _cnt_at(t[2], env)
            out.append((i, pos, n))
            pos += len(t[1]) * n
        else:
            break
    return out


def normalize_side_to(side, target, envs):
    """transform `side` (stream token list) into `target` by rotations, absorptions and peels of runs.
    Returns (newside, texts) or None."""
    side = list(side)
    texts = []
    runs_t = [t for t in target if is_run(t)]
    for step in range(200):
        if side == list(target):
            return side, texts
        runs_s = [t for t in side if is_run(t)]
        if len(runs_s) != len(runs_t):
            return None
        done_one = False
        for j in range(len(runs_s)):
            e = envs[0]
            ps = _run_positions(side, e)[j]
            pt = _run_positions(target, e)[j]
            i, s0, n0 = ps
            _, s1, n1 = pt
            ts = side[i]
            tt = runs_t[j]
            L = len(ts[1])
            ds = s1 - s0
            de = (s1 + L * n1) - (s0 + L * n0)
            # consistency over envs
            for e2 in envs[1:]:
                a = _run_positions(side, e2)[j]
                b = _run_positions(target, e2)[j]
                if b[1] - a[1] != ds or (b[1] + L * b[2]) - (a[1] + L * a[2]) != de:
                    return None
            if ds == 0 and de == 0:
                if ts != tt:
                    return None
                continue
            blk = ts[1]
            cnt = ts[2]
            # breadth-first search over elementary operations on this run
            def ops_of(sd, idx):
                t = sd[idx]
                bk = t[1]
                cn = t[2]
                res = []
                if idx >= L and all(isinstance(c, int) for c in sd[idx - L:idx]) and tuple(sd[idx - L:idx]) == bk:
                    ns, tx = absorb_side(sd, idx, 'near')
                    res.append((ns, idx - L, tx, (-3, 0)))
                if all(isinstance(c, int) for c in sd[idx + 1:idx + 1 + L]) and tuple(sd[idx + 1:idx + 1 + L]) == bk:
                    ns, tx = absorb_side(sd, idx, 'far')
                    res.append((ns, idx, tx, (0, 3)))
                if cn[0] >= 1 and (cn[1] or cn[0] - 1 > SMALL):
                    nc = cadd(cn, cconst(-1))
                    ns = sd[:idx] + list(bk) + [('run', bk, nc)] + sd[idx + 1:]
                    tx = "rewrite (lpow_peel_gen _ %s %s %s ltac:(kN_lia)). simpl." % (cl(bk), ccoq(cn), ccoq(nc))
                    res.append((ns, idx + L, tx, (3, 0)))
                    ns = sd[:idx] + [('run', bk, nc)] + list(bk) + sd[idx + 1:]
                    tx = "rewrite <- (absorbr3 %d %d %d %s %s _ ltac:(kN_lia))." % (bk + (ccoq(nc), ccoq(cn)))
                    res.append((ns, idx, tx, (0, -3)))
                if idx + 1 < len(sd) and isinstance(sd[idx + 1], int) and sd[idx + 1] == bk[0]:
                    a, b, c = bk
                    ns = sd[:idx] + [a, ('run', (b, c, a), cn)] + sd[idx + 2:]
                    res.append((ns, idx + 1, 'rewrite (rot3 %d %d %d %s _).' % (a, b, c, ccoq(cn)), (1, 1)))
                if idx >= 1 and isinstance(sd[idx - 1], int) and sd[idx - 1] == bk[-1]:
                    c = bk[-1]
                    a, b = bk[0], bk[1]
                    ns = sd[:idx - 1] + [('run', (c, a, b), cn), c] + sd[idx + 1:]
                    res.append((ns, idx - 1, 'rewrite <- (rot3 %d %d %d %s _).' % (c, a, b, ccoq(cn)), (-1, -1)))
                return res
            from collections import deque
            dq = deque([(side, i, (ds, de), [])])
            seen_st = {(ds, de, tuple(map(repr, side)))}
            found = None
            while dq:
                sd, idx, (a1, b1), tx = dq.popleft()
                if a1 == 0 and b1 == 0 and sd[idx][1] == tt[1] and sd[idx][2] == tt[2]:
                    found = (sd, tx)
                    break
                if len(tx) >= 8:
                    continue
                for ns, nidx, t1, (da, db) in ops_of(sd, idx):
                    st = (a1 - da, b1 - db)
                    key = (st[0], st[1], tuple(map(repr, ns)))
                    if key in seen_st:
                        continue
                    seen_st.add(key)
                    dq.append((ns, nidx, st, tx + [t1]))
            if found is None:
                return None
            side = found[0]
            texts.extend(found[1])
            side = norm_side(side)
            done_one = True
            break
        if not done_one:
            return (side, texts) if side == list(target) else None
    return None


def normalize_cfg_to(cfg, target):
    envs = [{v: 1000 + 37 * i for i, v in enumerate(sorted(set(vars_of(cfg)) | set(vars_of(target))))},
            {v: 2003 + 101 * i for i, v in enumerate(sorted(set(vars_of(cfg)) | set(vars_of(target))))}]
    q, L, R, mode = cfg
    q2, L2, R2, mode2 = target
    if q != q2 or mode != mode2:
        return None
    a = normalize_side_to(L, L2, envs)
    b = normalize_side_to(R, R2, envs)
    if a is None or b is None:
        return None
    return (q, a[0], b[0], mode), a[1] + b[1]
