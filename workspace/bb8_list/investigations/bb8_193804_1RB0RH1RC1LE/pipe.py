"""Pipeline crossing lemmas.  u-coordinates: head always travels toward decreasing u.
 '<' : u = physical position ; '>' : u = -physical position.
 xs : stream order (nearest the head first, head cell first); c : cells behind the head, nearest first.
 Lemma: xs^^n *> ahead  {{q}}  c >> r  -->*  ahead' {{q}} c >> ys^^n *> r   (c' == c required)."""
import planner8 as pl

def derive_pipe(q, direction, xs, c, maxsteps=100000):
    nx, nc = len(xs), len(c)
    P = list(reversed(xs)) + list(c)
    pos = nx - 1
    st = q
    sign = 1 if direction == '<' else -1
    for _ in range(maxsteps):
        if pos == -1:
            break
        if not (0 <= pos < len(P)):
            return None, 'left known region at %d (%s)' % (pos, st)
        tr = pl.T[(st, P[pos])]
        if tr is None:
            return None, 'halt'
        w, d, st = tr
        P[pos] = w
        pos += d * sign
    else:
        return None, 'loop'
    if st != q:
        return None, 'exit state %s != %s' % (st, q)
    Z = P
    if tuple(Z[:nc]) != tuple(c):
        return None, 'ctx changed %r -> %r' % (list(c), Z[:nc])
    return dict(q=q, dir=direction, xs=tuple(xs), c=tuple(c), ys=tuple(Z[nc:])), None

def pipe_name(lm):
    d = 'R' if lm['dir'] == '>' else 'L'
    return 'pp_%s%s_%s_%s_c%s' % (lm['q'], d, ''.join(map(str, lm['xs'])), ''.join(map(str, lm['ys'])), ''.join(map(str, lm['c'])))

PIPES = {}

def int_prefix(side):
    out = []
    for t in side:
        if isinstance(t, int):
            out.append(t)
        else:
            break
    return out

def pipe_matcher(NCS=range(4, 16)):
    """matcher for planner8.drive: apply a (derived on the fly) pipeline crossing lemma to a run under the head."""
    def m(cfg):
        q, L, R, mode = cfg
        run = L[0] if mode == '<' else R[0]
        if not pl.is_run(run):
            return None
        _, xs, cnt = run
        behind = R if mode == '<' else L
        direction = mode
        # concrete behind cells (BLANK terminator counts as zeros)
        conc = int_prefix(behind)
        if behind and behind[len(conc)] == pl.BLANK:
            conc = conc + [0] * 20
        for nc in NCS:
            if nc > len(conc):
                break
            c = conc[:nc]
            lm, why = derive_pipe(q, direction, xs, c)
            if lm:
                name = pipe_name(lm)
                PIPES[name] = lm
                nint = len(int_prefix(behind))
                rest = list(behind[min(nc, nint):])
                newbehind = list(c) + [('run', lm['ys'], cnt)] + rest
                if mode == '<':
                    new = (q, L[1:], pl.norm_side(newbehind), '<')
                else:
                    new = (q, pl.norm_side(newbehind), R[1:], '>')
                return new, 'follow %s.' % name, 'pipe %s x%s' % (name, pl.cnt_str(cnt))
        return None
    return m
