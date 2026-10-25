"""Turn engine.py proof trees into busycoq lemmas.

Conventions (they follow busycoq's simpl_tape normal form, which splits xs^^(n+m) into xs^^n *> xs^^m):
  * a run blk^(k + r) is written as one power per variable: [blk]^^k *> [blk]^^r *> rest;
  * a stage (literal steps, crossings, aligns between two configurations) becomes a lemma proved by the
    planner's script (do n step / follow crossing / align rewrites), closed by finish_norm;
  * a loop becomes  forall j ..., X(j) -->* X(0) with g^^j inserted, by induction on j: X(S j) is the peeled
    configuration the round was computed from, the round is replayed, and the induction hypothesis is used
    with the variable side behind the insertion instantiated to  g >> w.
"""
import planner8 as pl
from planner8 import BLANK, is_run

NL = '\n'


def cl(blk):
    return '[' + ';'.join(map(str, blk)) + ']'


def powers(blk, cnt, rest):
    """[blk]^^v1 *> [blk]^^v2 *> ... rest  (coefficients > 1 give c * v)."""
    out = rest
    for v, c in reversed(cnt):
        e = v if c == 1 else '(%d * %s)' % (c, v)
        out = '%s^^%s *> %s' % (cl(blk), e, out)
    return out


def side_coq(side, subst=None):
    """Coq stream for a planner side (tokens nearest the head first)."""
    subst = subst or {}
    toks = list(side)
    term = toks[-1]
    if term == BLANK:
        out = 'const 0'
    elif isinstance(term, tuple) and term[0] == 'VAR':
        out = subst.get(term[1], term[1])
    else:
        raise ValueError('side must end in a terminator: %r' % (term,))
    for t in reversed(toks[:-1]):
        if isinstance(t, int):
            out = '%d >> %s' % (t, out)
        elif is_run(t):
            out = powers(t[1], t[2], out)
        else:
            raise ValueError('unexpected token %r' % (t,))
    return out


def cfg_coq(cfg, subst=None):
    q, L, R, mode = cfg
    if mode == '>':
        return '(%s) {{%s}}> (%s)' % (side_coq(L, subst), q, side_coq(R, subst))
    return '(%s) <{{%s}} (%s)' % (side_coq(L, subst), q, side_coq(R, subst))


def free_vars(*cfgs):
    cnts, vs = set(), set()
    for q, L, R, mode in cfgs:
        for side in (L, R):
            for t in side:
                if is_run(t):
                    cnts.update(k for k, _ in t[2])
                elif isinstance(t, tuple) and t[0] == 'VAR':
                    vs.add(t[1])
    return sorted(cnts), sorted(vs)


def ops_to_tactics(ops):
    """Planner ops (steps / cross / align) -> tactic list for a -->* goal."""
    out = []
    for op in ops:
        if op[0] == 'steps':
            if op[1]:
                out.append('do %d step.' % op[1])
        elif op[0] == 'cross':
            out.extend(['follow %s.' % op[1]] * op[2])
        elif op[0] == 'align':
            kind, x0, xs, cnt = op[1]
            # every power of the run, whatever order crossings left them in (repeat: the inner one first)
            lem = 'align_lpow' if kind == 'ALIGN' else 'align_lpow_const'
            out.append('repeat rewrite (%s %d %s). simpl app.' % (lem, x0, cl(xs)))
        else:
            raise ValueError('op %r' % (op,))
    return out


def wrap(tactics, indent='  ', width=100):
    lines, line = [], indent
    for t in tactics:
        if len(line) + len(t) > width and line.strip():
            lines.append(line.rstrip())
            line = indent
        line += t + ' '
    if line.strip():
        lines.append(line.rstrip())
    return NL.join(lines)


def stage_lemma(name, start, ops, end, progress=False):
    cnts, vs = free_vars(start, end)
    binders = ' '.join(cnts + vs)
    stmt = '%s %s %s' % (cfg_coq(start), '-->+' if progress else '-->*', cfg_coq(end))
    if binders:
        stmt = 'forall %s, %s' % (binders, stmt)
    if progress:
        # the first literal step makes it a -->+ goal; the rest is the planner script as usual
        if not ops or ops[0][0] != 'steps' or ops[0][1] == 0:
            raise GenFail('a progress stage must start with a literal step')
        ops = [('steps', ops[0][1] - 1)] + list(ops[1:])
        tac = ['intros.', 'eapply progress_intro; [prove_step | simpl_tape].'] + ops_to_tactics(ops) + ['finish_norm.']
    else:
        tac = ['intros.'] + ops_to_tactics(ops) + ['finish_norm.']
    return 'Lemma %s : %s.\nProof.\n%s\nQed.\n' % (name, stmt, wrap(tac))


def crossing_lemmas():
    import coqgen_util
    return ''.join(coqgen_util.crossing_lemma(nm, pl.LEMMAS[nm]) + NL for nm in sorted(pl.LEMMAS))


# ---------------------------------------------------------------------------------------------- loops
def side_coq_custom(side, expo):
    """Like side_coq, with run exponents renamed through `expo` (e.g. {'j': '(S j)'})."""
    toks = list(side)
    term = toks[-1]
    out = 'const 0' if term == BLANK else term[1]
    for t in reversed(toks[:-1]):
        if isinstance(t, int):
            out = '%d >> %s' % (t, out)
        else:
            for v, c in reversed(t[2]):
                e = expo.get(v, v)
                e = e if c == 1 else '(%d * %s)' % (c, e)
                out = '%s^^%s *> %s' % (cl(t[1]), e, out)
    return out


def cfg_coq_custom(cfg, expo):
    q, L, R, mode = cfg
    if mode == '>':
        return '(%s) {{%s}}> (%s)' % (side_coq_custom(L, expo), q, side_coq_custom(R, expo))
    return '(%s) <{{%s}} (%s)' % (side_coq_custom(L, expo), q, side_coq_custom(R, expo))


class GenFail(Exception):
    pass


def loop_lemma(name, lp, engine):
    """Return (lemma text, use(cur_cfg_tokens) info). The lemma, for the loop found at lp['start'] on variable v:
        forall j <vars> <w..>, X(S j) -->* X(1) with g^^j inserted before w
    where X is the start configuration framed at each insertion point (the rest of that side becomes w)."""
    S, v, v2 = lp['start'], lp['v'], lp['v2']
    S1 = engine.subst(S, v, ((v2, 1),), 0)
    sides, rema, wnames = [], [], []
    for i in (1, 2):
        toks = engine.side_tokens(S1[i])
        pos, ins = lp['inserts'][i - 1]
        toks = [('run', t[1], tuple((('j' if k == v2 else k), c) for k, c in t[2])) if is_run(t) else t for t in toks]
        if ins:
            w = 'w%d_%s' % (i, name)
            rest = toks[pos:]
            if any(is_run(t) and any(k == 'j' for k, _ in t[2]) for t in rest):
                raise GenFail('loop variable beyond the insertion point')
            sides.append(toks[:pos] + [('VAR', w)])
            rema.append((w, rest, ins))
            wnames.append(w)
        else:
            sides.append(toks)
    Xb = (S1[0], pl.norm_side(sides[0]), pl.norm_side(sides[1]), S1[3])
    lhs = engine.subst(Xb, 'j', (('j', 1),), 1)          # [blk]^^(S j): one block peeled + run j
    step = engine.subst(Xb, 'j', (('j', 1),), 2)         # after simpl in the step case: two blocks peeled
    # one round: from two peeled blocks back to one, with g inserted right before each w
    expect_sides = []
    for i, (pos, ins) in zip((1, 2), lp['inserts']):
        toks = list(lhs[i])
        if ins:
            toks = toks[:-1] + list(ins) + [toks[-1]]
        expect_sides.append(pl.norm_side(toks))
    expect = (lhs[0], expect_sides[0], expect_sides[1], lhs[3])
    ops, C, how = engine.run_until_stuck(step, None, target=expect)
    round_text = ''
    if how != 'target':
        # The round contains loops of its own: a separate round lemma  X'(j) -->* X(j) + g  from one peeled block
        # (exactly the configuration the engine computed the round from), the inner loops run in full; it is used
        # with j := S j. (Two peeled blocks can be cut into blocks differently, and a crossing can then jump
        # over the end of the round.)
        try:
            Xr, _ = frame_loop(lp, engine, 'j', name)
            round_text, rname, rbind = nested_round_lemma(
                name + '_round', engine.subst(Xr, 'j', (('j', 1),), 1), before_w(Xr, lp['inserts'], lambda g: g),
                engine)
        except (engine.Fail, GenFail) as e:
            raise GenFail('framed round does not return to the loop shape (%s at %s); nested: %s'
                          % (how, pl.show(C), e))
        rargs = ' '.join('(S j)' if b == 'j' else b for b in rbind)
        ops = None
    # right-hand side: X(1) with g^^j right before each w
    rsides = []
    one = engine.subst(Xb, 'j', (), 1)
    for i, (pos, ins) in zip((1, 2), lp['inserts']):
        toks = list(one[i])
        if ins:
            toks = toks[:-1] + [('run', tuple(ins), (('j', 1),)), toks[-1]]
        rsides.append(pl.norm_side(toks))
    rhs = (one[0], rsides[0], rsides[1], one[3])
    cnts, vs = free_vars(Xb, rhs)
    cnts = [c for c in cnts if c != 'j']
    binders = ' '.join(['j'] + cnts + vs)
    lhs_s = cfg_coq_custom(engine.subst(Xb, 'j', (('j', 1),), 0), {'j': '(S j)'})
    stmt = 'forall %s, %s -->* %s' % (binders, lhs_s, cfg_coq(rhs))
    ih_args = []
    for c in cnts:
        ih_args.append(c)
    for w in vs:
        g = next((ins for (ww, _, ins) in rema if ww == w), None)
        ih_args.append('(%s%s)' % (''.join('%d >> ' % x for x in g), w) if g else w)
    # helper per insertion: the block the induction hypothesis leaves in front of w moves behind the power
    helpers, shifts = '', []
    for k, (w, _, g) in enumerate(rema):
        hn = '%s_sh%d' % (name, k + 1)
        cells = ''.join('%d >> ' % x for x in g)
        helpers += ("Lemma %s : forall n (Y : side), %s^^n *> (%sY) = %s%s^^n *> Y.\n"
                    "Proof. intros. change (%sY) with (%s *> Y). rewrite lpow_shift'. reflexivity. Qed.\n\n"
                    % (hn, cl(g), cells, cells, cl(g), cells, cl(g)))
        shifts.append('rewrite ?%s.' % hn)
    if ops is None:
        # the round lemma ends exactly at the induction hypothesis' start (no align_tape in between)
        tac = ['induction j; intros.', '- simpl. finish_norm.', '- simpl.', 'follow (%s %s).' % (rname, rargs),
               'follow (IHj %s).' % ' '.join(ih_args)] + shifts + ['finish_norm.']
    else:
        tac = ['induction j; intros.', '- simpl. finish_norm.', '- simpl.'] + ops_to_tactics(ops) + \
              ['try align_tape.', 'follow (IHj %s).' % ' '.join(ih_args)] + shifts + ['finish_norm.']
    text = helpers + round_text + 'Lemma %s : %s.\nProof.\n%s\nQed.\n' % (name, stmt, wrap(tac))
    return text, dict(cnts=cnts, vs=vs, rema=rema, rhs=rhs)


# ---------------------------------------------------------------------------------------------- nested loops
def frame_loop(lp, engine, jn, name):
    """The loop's start configuration with the loop variable renamed jn, each side cut at its insertion point
    (the rest of that side becomes the variable w<i>_<name>). Returns (Xb, rema = [(w, rest tokens, block)])."""
    S, v, v2 = lp['start'], lp['v'], lp['v2']
    S1 = engine.subst(S, v, ((v2, 1),), 0)
    sides, rema = [], []
    for i in (1, 2):
        toks = engine.side_tokens(S1[i])
        pos, ins = lp['inserts'][i - 1]
        toks = [('run', t[1], tuple(((jn if k == v2 else k), c) for k, c in t[2])) if is_run(t) else t for t in toks]
        if ins:
            w = 'w%d_%s' % (i, name)
            rest = toks[pos:]
            if any(is_run(t) and any(k == jn for k, _ in t[2]) for t in rest):
                raise GenFail('loop variable beyond the insertion point')
            sides.append(toks[:pos] + [('VAR', w)])
            rema.append((w, rest, ins))
        else:
            sides.append(toks)
    return (S1[0], pl.norm_side(sides[0]), pl.norm_side(sides[1]), S1[3]), rema


def before_w(cfg, inserts, mk):
    """Put mk(block) right before the frame variable of every side with an insertion."""
    sides = []
    for i, (pos, ins) in zip((1, 2), inserts):
        toks = list(cfg[i])
        if ins:
            toks = toks[:-1] + list(mk(ins)) + [toks[-1]]
        sides.append(pl.norm_side(toks))
    return (cfg[0], sides[0], sides[1], cfg[3])


def instantiate(cfg, sub):
    """Replace frame variables by token lists (the configuration at the call site of a framed lemma)."""
    sides = []
    for side in (cfg[1], cfg[2]):
        toks = list(side)
        if isinstance(toks[-1], tuple) and toks[-1][0] == 'VAR' and toks[-1][1] in sub:
            toks = toks[:-1] + list(sub[toks[-1][1]])
        sides.append(pl.norm_side(toks))
    return (cfg[0], sides[0], sides[1], cfg[3])


def full_loop_lemma(name, lp, engine, depth=0):
    """A loop run in full, for use inside the round of an outer loop:
        forall j <vars> <w..>, X(j) -->* X(0) with g^^j inserted before w.
    Valid for every j: the round was computed from X(j'+1) with j' symbolic and returns to X(j') + g.
    Returns (text, info); info['call'] is the argument list at the place the loop was found, info['after'] the
    configuration the lemma leaves there."""
    S, v = lp['start'], lp['v']
    others = set(free_vars(S)[0]) - {v}
    jn = next(c for c in ('j', 'i', 'm', 'j0', 'j1', 'j2', 'j3') if c not in others)
    Xb, rema = frame_loop(lp, engine, jn, name)
    step = engine.subst(Xb, jn, ((jn, 1),), 1)          # X(S j) after simpl: one block peeled
    expect = before_w(Xb, lp['inserts'], lambda g: g)
    rhs = before_w(engine.subst(Xb, jn, (), 0), lp['inserts'], lambda g: [('run', tuple(g), ((jn, 1),))])
    cnts, vs = free_vars(Xb, rhs)
    cnts = [c for c in cnts if c != jn]
    stmt = 'forall %s, %s -->* %s' % (' '.join([jn] + cnts + vs), cfg_coq(Xb), cfg_coq(rhs))
    ops, C, how = engine.run_until_stuck(step, None, target=expect)
    round_text = ''
    if how == 'target':
        round_tac = ops_to_tactics(ops) + ['try align_tape.']
    elif depth > 0:
        round_text, rname, rbind = nested_round_lemma(name + '_round', step, expect, engine, depth - 1)
        round_tac = ['follow (%s %s).' % (rname, ' '.join(rbind))]
    else:
        raise GenFail('inner loop %s: framed round does not return to the loop shape (%s at %s)'
                      % (name, how, pl.show(C)))
    ih_args = list(cnts)
    for w in vs:
        g = next((ins for (ww, _, ins) in rema if ww == w), None)
        ih_args.append('(%s%s)' % (''.join('%d >> ' % x for x in g), w) if g else w)
    helpers, shifts = '', []
    for k, (w, _, g) in enumerate(rema):
        hn = '%s_sh%d' % (name, k + 1)
        cells = ''.join('%d >> ' % x for x in g)
        helpers += ("Lemma %s : forall n (Y : side), %s^^n *> (%sY) = %s%s^^n *> Y.\n"
                    "Proof. intros. change (%sY) with (%s *> Y). rewrite lpow_shift'. reflexivity. Qed.\n\n"
                    % (hn, cl(g), cells, cells, cl(g), cells, cl(g)))
        shifts.append('rewrite ?%s.' % hn)
    tac = ['induction %s; intros.' % jn, '- simpl. finish_norm.', '- simpl.'] + round_tac + \
          ['follow (IH%s %s).' % (jn, ' '.join(ih_args))] + shifts + ['finish_norm.']
    text = helpers + round_text + 'Lemma %s : %s.\nProof.\n%s\nQed.\n' % (name, stmt, wrap(tac))
    sub = {w: rest for w, rest, _ in rema}
    call = [v] + cnts + [('(%s)' % side_coq(sub[w])) if w in sub else w for w in vs]
    after = instantiate(engine.subst(rhs, jn, ((v, 1),), 0), sub)
    return text, dict(cnts=cnts, vs=vs, rema=rema, call=call, after=after)


def nested_round_lemma(name, start, target, engine, depth=0):
    """start -->* target for a round that contains loops: stage lemmas between them, each inner loop by
    full_loop_lemma. Returns (text, lemma name, binder names in order)."""
    segs = engine.run_nested(start, target, depth)
    texts, tac = [], ['intros.']
    k = 0
    cur = start
    for seg in segs:
        if seg[0] == 'ops':
            ops, end = seg[1], seg[3]
            k += 1
            sname = '%s_st%d' % (name, k)
            texts.append(stage_lemma(sname, cur, ops, end))
            tac.append('follow %s.' % sname)
        else:
            lp = seg[1]
            k += 1
            iname = '%s_in%d' % (name, k)
            text, info = full_loop_lemma(iname, lp, engine, depth)
            texts.append(text)
            tac.append('follow (%s %s).' % (iname, ' '.join(info['call'])))
            if cfg_coq(info['after']) != cfg_coq(lp['result']):
                raise GenFail('inner loop %s: lemma result %s differs from the explored %s'
                              % (iname, pl.show(info['after']), pl.show(lp['result'])))
            cur = info['after']
    tac.append('finish_norm.')
    cnts, vs = free_vars(start, target)
    binders = cnts + vs
    stmt = '%s -->* %s' % (cfg_coq(start), cfg_coq(target))
    if binders:
        stmt = 'forall %s, %s' % (' '.join(binders), stmt)
    texts.append('Lemma %s : %s.\nProof.\n%s\nQed.\n' % (name, stmt, wrap(tac)))
    return '\n'.join(texts) + '\n', name, binders


# ---------------------------------------------------------------------------------------------- rules
class RuleGen:
    def __init__(self, prefix, engine):
        self.prefix, self.engine, self.lemmas, self.n = prefix, engine, [], 0

    def name(self, kind):
        self.n += 1
        return '%s_%s%d' % (self.prefix, kind, self.n)

    def stage(self, a, ops, b, progress=False):
        nm = self.name('st')
        self.lemmas.append(stage_lemma(nm, a, ops, b, progress))
        if progress:
            return 'eapply progress_evstep_trans; [apply %s |].' % nm
        return 'follow %s.' % nm

    BULLETS = ['-', '+', '*', '--', '++', '**', '---', '+++', '***']

    def node(self, node, ind, depth=0, progress=False):
        """Tactic lines proving node['start'] -->* node['target'] (-->+ when progress: the first stage is then a
        -->+ lemma)."""
        bul = self.BULLETS[depth]
        items = node['items']
        out = []
        for k, it in enumerate(items):
            if it[0] == 'ops':
                _, ops, a, b = it
                last = k == len(items) - 1
                if last:
                    out.append(ind + self.stage(a, ops, b, progress))
                    out.append(ind + 'finish_norm.')
                    return out
                nxt = items[k + 1]
                v, v2 = (nxt[1]['v'], nxt[1]['v2']) if nxt[0] == 'loop' else (nxt[1], nxt[2])
                out.append(ind + 'destruct %s as [| %s].' % (v, v2))
                b0, b1 = (nxt[2], nxt[3]) if nxt[0] == 'loop' else (nxt[3], nxt[4])
                if b0 is None:
                    out.append(ind + bul + ' lia.')          # excluded: hypothesis 0 < v (rule_lemma positive)
                else:
                    out.append(ind + bul + ' simpl.')
                    out.extend(self.node(b0, ind + '  ', depth + 1, progress))
                out.append(ind + bul + ' idtac.')
                if nxt[0] == 'loop':
                    lp = nxt[1]
                    # the stage lemma is general in v; Coq instantiates v := S v2 (the goal is not simplified)
                    out.append(ind + '  ' + self.stage(a, ops, b, progress))
                    progress = False
                    nm = self.name('loop')
                    text, info = loop_lemma(nm, lp, self.engine)
                    self.lemmas.append(text)
                    rem = {w: self._rema(w, r, info) for w, r, _ in info['rema']}
                    args = [v2] + info['cnts'] + [rem.get(w, w) for w in info['vs']]
                    out.append(ind + '  follow (%s %s).' % (nm, ' '.join(args)))
                else:
                    out.append(ind + '  simpl.')
                out.extend(self.node(b1, ind + '  ', depth + 1, progress))
                return out
        raise GenFail('node without a final stage')

    def _rema(self, w, rest, info):
        # the rest of the side behind the insertion point, as a Coq stream
        return '(%s)' % side_coq(list(rest))


def rule_lemma(name, start, target, tree, gen, progress=True, positive=()):
    """positive: the variables explored with explore(..., positive=...); each gets a hypothesis (Hpos_v : 0 < v)."""
    lines = gen.node(tree, '  ', 0, progress)
    cnts, vs = free_vars(start, target)
    binders = ' '.join(cnts + vs + ['(Hpos_%s : 0 < %s)' % (v, v) for v in sorted(positive)])
    stmt = '%s %s %s' % (cfg_coq(start), '-->+' if progress else '-->*', cfg_coq(target))
    if binders:
        stmt = 'forall %s, %s' % (binders, stmt)
    return 'Lemma %s : %s.\nProof.\n  intros.\n%s\nQed.\n' % (name, stmt, NL.join(lines))
