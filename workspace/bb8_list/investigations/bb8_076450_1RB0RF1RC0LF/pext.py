"""Extensions to planner8: sweeps whose small context travels with the head (reads ahead / behind)."""
import planner8 as P

SWEEPS = {}

def derive_sweep(q, direction, xs, behind, k):
    """Context = first k cells of `behind` (stream order, away from the block).
    '>' : tape [ctx_tape (k)] [xs_tape (b)] with head on first block cell -> after: [out (b)] [ctx (k)], head just right, state q.
    '<' : mirror."""
    if len(behind) < k:
        return None
    b = len(xs)
    ctx = list(behind[:k])              # stream order (nearest head first)
    if direction == '>':
        tape = list(reversed(ctx)) + list(xs)
        pos = k; exit_pos = k + b
    else:
        tape = list(reversed(xs)) + ctx
        pos = b - 1; exit_pos = -1
    st = q
    for _ in range(2000):
        if pos == exit_pos:
            break
        if not (0 <= pos < len(tape)):
            return None
        tr = P.T[(st, tape[pos])]
        if tr is None:
            return None
        w, d, st = tr
        tape[pos] = w; pos += d
    else:
        return None
    if st != q:
        return None
    if direction == '>':
        # after: tape = [out (b)] [ctx_tape (k)]
        if tape[b:] != list(reversed(ctx)):
            return None
        out_tape = tape[:b]
        out_stream = list(reversed(out_tape))    # stream order for the left side
    else:
        # after: tape = [ctx_tape (k)] [out (b)] ; ctx_tape = reversed(ctx) for right side? right stream order = tape order
        if tape[:k] != ctx:
            return None
        out_stream = tape[k:]
    return dict(q=q, dir=direction, xs=tuple(xs), ys=tuple(out_stream), ctx=tuple(ctx))

def sweep_name(lm):
    d = 'R' if lm['dir'] == '>' else 'L'
    return 'sw_%s%s_%s_%s_c%s' % (lm['q'], d, ''.join(map(str, lm['xs'])), ''.join(map(str, lm['ys'])), ''.join(map(str, lm['ctx'])))

def m_sweep(cfg):
    q, L, R, mode = cfg
    run = R[0] if mode == '>' else L[0]
    if not P.is_run(run):
        return None
    r, why = P.try_crossing(cfg)
    if r:
        return None
    behind = P.concrete_prefix(L if mode == '>' else R)
    _, xs, cnt = run
    for k in range(1, 7):
        lm = derive_sweep(q, mode, xs, behind, k)
        if lm is None:
            continue
        name = sweep_name(lm)
        SWEEPS[name] = lm
        if mode == '>':
            # L = ctx + rest ; new L = ctx + run(ys) + rest
            newL = list(L[:k]) + [('run', lm['ys'], cnt)] + list(L[k:])
            cfg2 = (q, P.norm_side(newL), P.norm_side(R[1:]), '>')
        else:
            newR = list(R[:k]) + [('run', lm['ys'], cnt)] + list(R[k:])
            cfg2 = (q, P.norm_side(L[1:]), P.norm_side(newR), '<')
        return cfg2, 'follow %s.' % name, 'sweep %s (x%s)' % (name, P.cnt_str(cnt))
    return None

def sweep_lemma(name, lm):
    q, d, xs, ys, ctx = lm['q'], lm['dir'], lm['xs'], lm['ys'], lm['ctx']
    cl = lambda t: '[' + ';'.join(map(str, t)) + ']'
    if d == '>':
        stmt = 'forall n l r, (%s *> l) {{%s}}> %s^^n *> r -->* (%s *> %s^^n *> l) {{%s}}> r' % (cl(ctx), q, cl(xs), cl(ctx), cl(ys), q)
    else:
        stmt = 'forall n l r, %s^^n *> l <{{%s}} (%s *> r) -->* l <{{%s}} (%s *> %s^^n *> r)' % (cl(xs), q, cl(ctx), q, cl(ctx), cl(ys))
    return ('Lemma %s : %s.\nProof. induction n; intros. - finish. - execute. follow IHn. finish_norm. Qed.\n' % (name, stmt))


def _concrete(side):
    out = []
    for t in side:
        if isinstance(t, int):
            out.append(t)
        else:
            break
    return out


def m_concrete(cfg):
    """Cross (or sweep over) >= 2 concrete copies of a block in one lemma application with a numeral count."""
    q, L, R, mode = cfg
    ahead = _concrete(R if mode == '>' else L)
    behind = _concrete(L if mode == '>' else R)
    best = None
    for b in range(1, 7):
        xs = tuple(ahead[:b])
        if len(xs) < b:
            break
        c = 1
        while tuple(ahead[c * b:(c + 1) * b]) == xs:
            c += 1
        if c < 2 or c * b < 4:
            continue
        if best is None or c * b > best[1] * len(best[0]):
            best = (xs, c)
    if best is None:
        return None
    xs, c = best
    b = len(xs)
    lm, why = P.derive_crossing(q, mode, xs, behind)
    if lm is not None and len(lm['ctx']) <= len(behind):
        name = P.lemma_name(lm)
        P.LEMMAS[name] = lm
        ys = list(lm['ys'])
        if mode == '>':
            cfg2 = (q, P.norm_side(ys * c + L), P.norm_side(R[b * c:]), '>')
        else:
            cfg2 = (q, P.norm_side(L[b * c:]), P.norm_side(ys * c + R), '<')
        return cfg2, 'follow (%s %d).' % (name, c), 'cross %s x%d (concrete)' % (name, c)
    for k in range(1, 7):
        if k > len(behind):
            break
        lm = derive_sweep(q, mode, xs, behind, k)
        if lm is None:
            continue
        name = sweep_name(lm)
        SWEEPS[name] = lm
        ys = list(lm['ys'])
        if mode == '>':
            cfg2 = (q, P.norm_side(list(L[:k]) + ys * c + list(L[k:])), P.norm_side(R[b * c:]), '>')
        else:
            cfg2 = (q, P.norm_side(L[b * c:]), P.norm_side(list(R[:k]) + ys * c + list(R[k:])), '<')
        return cfg2, 'follow (%s %d).' % (name, c), 'sweep %s x%d (concrete)' % (name, c)
    return None
m_concrete.anytime = True
