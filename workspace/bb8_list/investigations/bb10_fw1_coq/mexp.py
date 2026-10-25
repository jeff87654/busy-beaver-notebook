"""Macro explorer: symbolic execution with "transfer" loops, for busycoq proofs of machine #11.

autoproof's engine finds a loop when a round peels one block of a run (variable v) and comes back to the same
configuration with one concrete block g inserted on a side; coqgen then frames the side at the insertion point,
which fails when the round itself crosses the growing stack. Here the stack is a run of its own:

  X(v, i) = the stuck configuration with v renamed and a run g^i at each insertion point;
  round:  X(S v, i) -->* X(v, S i)     (proved by symbolic execution on the generalised configuration, which must
                                          cross the g^i runs with crossing lemmas; inner loops are allowed)
  loop:   X(v, i)   -->* X(0, i + v)   (induction on v, i general)

At the use site i = 0, so the loop turns S into S with v -> 0 and g^v inserted.
"""
import itertools
import random
from common import *
from planner8 import is_run, is_term, norm_side, canon, show, expand_side, lin, lin_add, Stuck, Halted

FRESH = itertools.count()


def fresh(base):
    return '%s%d' % (base.rstrip('0123456789_'), next(FRESH))


subst = engine.subst
vars_of = engine.vars_of
coeff_ok = engine.coeff_ok
side_tokens = engine.side_tokens


class Fail(Exception):
    pass


def run_stuck(cfg, target=None, budget=400000):
    return engine.run_until_stuck(cfg, canon(target) if target is not None else None, budget=budget, target=target)


# ------------------------------------------------------------------------------------------------ loops
def match_side_multi(s, c, maxgaps=4, maxlen=64):
    """c = s with concrete blocks inserted at up to maxgaps places. Returns [(pos in s, inserted tuple)] or None.
    Cost: 1000 per gap, +1 when the inserted block is not a copy of its neighbourhood in c (a gap inside a
    periodic stretch, next to a copy of itself, is the natural place for a stack)."""
    n, m = len(s), len(c)
    INF = 10 ** 9

    def pen(j1, j2):
        g = c[j1:j2]
        L = j2 - j1
        if tuple(c[j2:j2 + L]) == tuple(g) or (j1 >= L and tuple(c[j1 - L:j1]) == tuple(g)):
            return 0
        return 1
    best = [[INF] * (m + 1) for _ in range(n + 1)]
    choice = [[None] * (m + 1) for _ in range(n + 1)]
    best[n][m] = 0
    for i in range(n, -1, -1):
        for j in range(m, -1, -1):
            if i == n and j == m:
                continue
            v, ch = INF, None
            if i < n and j < m and s[i] == c[j] and best[i + 1][j + 1] < INF:
                v, ch = best[i + 1][j + 1], ('m',)
            # a gap c[j:j2] (only directly before a matched token or at the end)
            j2 = j
            while j2 < m and j2 - j < maxlen and isinstance(c[j2], int):
                j2 += 1
                nxt = best[i][j2] if (j2 == m and i == n) else (best[i + 1][j2 + 1] if i < n and j2 < m and s[i] == c[j2] else INF)
                if nxt < INF:
                    cost = nxt + 1000 + pen(j, j2)
                    if cost < v:
                        v, ch = cost, ('g', j2)
            best[i][j], choice[i][j] = v, ch
    if best[0][0] >= (maxgaps + 1) * 1000:
        return None
    out, i, j = [], 0, 0
    while i < n or j < m:
        ch = choice[i][j]
        if ch[0] == 'm':
            i += 1; j += 1
        else:
            out.append((i, tuple(c[j:ch[1]])))
            j = ch[1]
            if i < n:
                i += 1; j += 1
    return out


def match_shift_multi(S1, C):
    if S1[0] != C[0] or S1[3] != C[3]:
        return None
    res = []
    for i in (1, 2):
        r = match_side_multi(side_tokens(S1[i]), side_tokens(C[i]))
        if r is None:
            return None
        res.append(r)
    return res


class Loop:
    """X: generalised configuration (loop variable vg, stack variables ivs); segs: the round
    X(S vg2) -> X(vg2, S i) as segments [('ops', ops, a, b) | ('loop', Loop, at, after)]."""
    def __init__(self, **kw):
        self.__dict__.update(kw)

    def after(self):
        """Configuration after all rounds, at the use site (loop count = use = (lin form, const))."""
        form, const = self.use
        c = subst(self.X, self.vg, (), 0)
        for iv in self.ivs:
            c = subst(c, iv, form, const)
        return c

    def use_arg(self):
        form, const = self.use
        s = ' + '.join(v if c == 1 else '%d * %s' % (c, v) for v, c in form) or '0'
        return '(%d + %s)' % (const, s) if const else s

    def others(self):
        cn, vs = coqgen.free_vars(self.X)
        return [c for c in cn if c != self.vg and c not in self.ivs], vs


def insert_variants(found):
    """The matched insertions, then each gap split in two (two stacks growing side by side)."""
    yield found
    for side in (0, 1):
        for k, (pos, g) in enumerate(found[side]):
            for cut in range(1, len(g)):
                alt = [list(found[0]), list(found[1])]
                alt[side][k] = (pos, [tuple(g[:cut]), tuple(g[cut:])])
                yield alt


def generalize(S, v, inserts):
    """inserts: per side a list [(pos, block)]; each block gets a stack run g^i at its position."""
    vg = fresh('n')
    S1 = subst(S, v, ((vg, 1),), 0)
    sides, ivs = [], []
    for i in (1, 2):
        toks = side_tokens(S1[i])
        for pos, ins in sorted(inserts[i - 1], key=lambda x: x[0], reverse=True):
            blocks = ins if (ins and isinstance(ins[0], tuple)) else [ins]
            runs = []
            for b in blocks:
                if b:
                    iv = fresh('i')
                    ivs.append(iv)
                    runs.append(('run', tuple(b), ((iv, 1),)))
            toks = toks[:pos] + runs + toks[pos:]
        sides.append(norm_side(toks))
    return (S1[0], sides[0], sides[1], S1[3]), vg, ivs


MAXSUB = 40


def run_round(P, target, depth, maxloops=40):
    """Execute from P to target, running inner loops in full. Returns segments or None."""
    segs, cfg = [], P
    for _ in range(maxloops + 1):
        a = cfg
        try:
            ops, cfg, how = run_stuck(cfg, target)
        except (engine.Fail, RuntimeError):
            return None
        segs.append(('ops', ops, a, cfg))
        if how == 'target':
            return segs
        if how != 'stuck' or depth <= 0:
            return None
        lp = find_loop(cfg, depth - 1)
        if lp is None:
            return None
        after = lp.after()
        segs.append(('loop', lp, cfg, after))
        cfg = after
    return None


def absorb_variants(S):
    """(S', v, (form, const)): the stuck configuration with j >= 0 concrete copies in front of the run under the head
    absorbed into the run (a fresh count variable v = old count + j); the use site then has v := j + old count."""
    out = []
    for v in engine.candidates(S):
        if coeff_ok(S, v):
            out.append((S, v, (((v, 1),), 0)))
    q, L, R, mode = S
    front = R if mode == '>' else L
    p = 0
    while p < len(front) and isinstance(front[p], int):
        p += 1
    if p < len(front) and is_run(front[p]) and len(front[p][2]) == 1 and front[p][2][0][1] == 1:
        _, blk, cnt = front[p]
        k = cnt[0][0]
        uses = sum(1 for side in (L, R) for t in side if is_run(t) and any(x == k for x, _ in t[2]))
        n = len(blk)
        j = 0
        while uses == 1 and (j + 1) * n <= p and tuple(front[p - (j + 1) * n:p - j * n]) == tuple(blk):
            j += 1
            w = fresh(k)
            side = list(front[:p - j * n]) + [('run', blk, ((w, 1),))] + list(front[p + 1:])
            S2 = (q, L, side, mode) if mode == '>' else (q, side, R, mode)
            out.append((S2, w, (((k, 1),), j)))
    return out


def find_loop(S, depth=1, verbose=False):
    """Simple loops first (no inner loops), then nested ones."""
    for d in range(depth + 1):
        for S2, v, use in absorb_variants(S):
            lp = try_loop(S2, v, d, verbose)
            if lp is not None:
                lp.S, lp.use = S, use
                return lp
    return None


def try_loop(S, v, depth, verbose=False):
    v2 = fresh(v)
    P = subst(S, v, ((v2, 1),), 1)
    S1 = subst(S, v, ((v2, 1),), 0)
    cfg = P
    found = None
    nsteps = 0
    for _ in range(MAXSUB):
        try:
            ops, C, how = run_stuck(cfg)
        except (engine.Fail, RuntimeError):
            break
        if how != 'stuck':
            break
        nsteps += sum(o[1] for o in ops if o[0] == 'steps') + sum(1 for o in ops if o[0] == 'cross')
        if nsteps == 0:
            break
        m = match_shift_multi(S1, C)
        if m is not None and any(ins for side in m for _, ins in side):
            found = m
            break
        if depth <= 0:
            break
        inner = find_loop(C, depth - 1)
        if inner is None:
            break
        cfg = inner.after()
    if found is None:
        return None
    for ins in insert_variants(found):
        X, vg, ivs = generalize(S, v, ins)
        vg2 = fresh(vg)
        Xp = subst(X, vg, ((vg2, 1),), 1)
        Xt = subst(X, vg, ((vg2, 1),), 0)
        for iv in ivs:
            Xt = subst(Xt, iv, ((iv, 1),), 1)
        segs = run_round(Xp, Xt, depth)
        if segs is not None:
            break
        if verbose:
            print('  loop on %s: generalised round fails for inserts %s' % (v, ins))
    else:
        return None
    return Loop(X=X, vg=vg, vg2=vg2, ivs=ivs, Xp=Xp, Xt=Xt, segs=segs, v_at=v, S=S, use=(((v, 1),), 0))


# ------------------------------------------------------------------------------------------------ exploration
def explore(start, target, depth=2, splits=6, positive=frozenset(), path='root', maxstages=60):
    node = {'start': start, 'target': target, 'items': [], 'path': path}
    cfg = start
    for _ in range(maxstages):
        a = cfg
        ops, cfg, how = run_stuck(cfg, target)
        node['items'].append(('ops', ops, a, cfg))
        if how == 'target':
            node['end'] = cfg
            return node
        if how == 'halt':
            if target is None:
                node['end'] = cfg
                node['halt'] = True
                return node
            raise Fail('%s: halted at %s' % (path, show(cfg)))
        lp = find_loop(cfg, depth)
        if lp is not None:
            after = lp.after()
            node['items'].append(('loop', lp, cfg, after))
            cfg = after
            continue
        if splits <= 0:
            raise Fail('%s: stuck without loop at %s' % (path, show(cfg)))
        _, why = pl.try_crossing(cfg)
        cand = engine.candidates(cfg, behind_first=bool(why) and why.startswith('left known region'))
        cand = [c for c in cand if coeff_ok(a, c)] or cand
        if not cand:
            raise Fail('%s: stuck, no variable at %s' % (path, show(cfg)))
        v = cand[0]
        v2 = fresh(v)
        # SPLIT AT THE NODE START (local change, bb10_lead_0LJ0LC): splitting at the stage start is unsound for the
        # v = 0 branch when an earlier stage already ran past the target for v = 0 (the target is only checked for
        # the symbolic configuration). Restarting the node from its start with v split avoids that.
        node['items'] = []
        a = start
        b0 = None
        if v not in positive:
            b0 = explore(subst(a, v, (), 0), subst(target, v, (), 0) if target is not None else None, depth, splits - 1, positive, path + '/%s=0' % v, maxstages)
        pos2 = (positive | {v2}) if v in positive else positive
        b1 = explore(subst(a, v, ((v2, 1),), 1), subst(target, v, ((v2, 1),), 1) if target is not None else None, depth, splits - 1, pos2,
                     path + '/%s=S%s' % (v, v2), maxstages)
        node['items'].append(('split', v, v2, b0, b1, a))
        return node
    raise Fail('%s: too many stages' % path)


def describe(node, ind=''):
    out = [ind + 'from: ' + show(node['start'])]
    for it in node['items']:
        if it[0] == 'ops':
            out.append(ind + '  ops: ' + ' '.join(o[0] if o[0] != 'steps' else 's%d' % o[1] for o in it[1]))
        elif it[0] == 'loop':
            out.extend(describe_loop(it[1], ind + '  '))
            out.append(ind + '  after loop: ' + show(it[3]))
        elif it[0] == 'split':
            out.append(ind + '  SPLIT %s' % it[1])
            out.extend(describe(it[3], ind + '    ') if it[3] is not None else [ind + '    (%s = 0 excluded)' % it[1]])
            out.extend(describe(it[4], ind + '    '))
    if 'end' in node:
        out.append(ind + 'reached: ' + show(node['end']))
    return out


def describe_loop(lp, ind):
    out = [ind + 'LOOP on %s (stacks %s): X = %s' % (lp.v_at, lp.ivs, show(lp.X))]
    for s in lp.segs:
        if s[0] == 'ops':
            out.append(ind + '   round ops: ' + ' '.join(o[0] if o[0] != 'steps' else 's%d' % o[1] for o in s[1]))
        else:
            out.extend(describe_loop(s[1], ind + '   '))
    return out


# ------------------------------------------------------------------------------------------------ Coq
cfg_coq = coqgen.cfg_coq
NL = '\n'


class Gen:
    def __init__(self, prefix):
        self.prefix, self.lemmas, self.n = prefix, [], 0
        self.done = {}

    def name(self, kind):
        self.n += 1
        return '%s_%s%d' % (self.prefix, kind, self.n)

    def stage(self, a, ops, b, progress=False):
        nm = self.name('st')
        self.lemmas.append(coqgen.stage_lemma(nm, a, ops, b, progress))
        if progress:
            return 'eapply progress_evstep_trans; [apply %s |].' % nm
        return 'follow %s.' % nm

    def loop(self, lp):
        """Emit the round and loop lemmas once; return (loop lemma name, binder list)."""
        if id(lp) in self.done:
            return self.done[id(lp)]
        cn, vs = lp.others()
        binders = [lp.vg] + lp.ivs + cn + vs
        # round lemma: Xp -->* Xt (segments)
        rname = self.name('round')
        tac = ['intros.']
        for s in lp.segs:
            if s[0] == 'ops':
                tac.append(self.stage(s[2], s[1], s[3]))
            else:
                tac.append(self.use_loop(s[1]))
        tac.append('finish_norm.')
        rb = [lp.vg2] + lp.ivs + cn + vs
        self.lemmas.append('Lemma %s : forall %s, %s -->* %s.\nProof.\n%s\nQed.\n'
                           % (rname, ' '.join(rb), cfg_coq(lp.Xp), cfg_coq(lp.Xt), coqgen.wrap(tac)))
        lname = self.name('loop')
        rhs = subst(lp.X, lp.vg, (), 0)
        for iv in lp.ivs:
            rhs = subst(rhs, iv, ((iv, 1), (lp.vg, 1)), 0)
        ih = ' '.join(['(S %s)' % iv for iv in lp.ivs] + cn + vs)
        tac = ['induction %s; intros.' % lp.vg, '- finish_norm.',
               '- follow (%s %s).' % (rname, ' '.join([lp.vg] + lp.ivs + cn + vs)),
               '  follow (IH%s %s).' % (lp.vg, ih), '  finish_norm.']
        self.lemmas.append('Lemma %s : forall %s, %s -->* %s.\nProof.\n%s\nQed.\n'
                           % (lname, ' '.join(binders), cfg_coq(lp.X), cfg_coq(rhs), NL.join('  ' + t for t in tac)))
        self.done[id(lp)] = (lname, binders)
        return self.done[id(lp)]

    def use_loop(self, lp):
        """A corollary at the use site (i = 0 baked in), stated with the explorer's configurations."""
        lname, binders = self.loop(lp)
        args = [lp.use_arg()] + ['0'] * len(lp.ivs) + binders[1 + len(lp.ivs):]
        zname = lname + '_z'
        if zname not in self.done:
            after = lp.after()
            cn, vs = coqgen.free_vars(lp.S, after)
            self.lemmas.append('Lemma %s : forall %s, %s -->* %s.\nProof.\n  intros. follow (%s %s). finish_norm.\nQed.\n'
                               % (zname, ' '.join(cn + vs), cfg_coq(lp.S), cfg_coq(after), lname, ' '.join(args)))
            self.done[zname] = True
        return 'follow %s.' % zname

    BUL = ['-', '+', '*', '--', '++', '**', '---', '+++', '***', '----']

    def node(self, node, ind='  ', depth=0, progress=False):
        out = []
        items = node['items']
        for k, it in enumerate(items):
            if it[0] == 'ops':
                _, ops, a, b = it
                if progress and not any(o[0] == 'steps' and o[1] for o in ops[:1]):
                    raise Fail('progress stage must start with a literal step')
                out.append(ind + self.stage(a, ops, b, progress))
                progress = False
            elif it[0] == 'loop':
                if progress:
                    raise Fail('progress rule starting with a loop')
                out.append(ind + self.use_loop(it[1]))
            elif it[0] == 'split':
                _, v, v2, b0, b1, a = it
                bul = self.BUL[depth]
                out.append(ind + 'destruct %s as [| %s].' % (v, v2))
                if b0 is None:
                    out.append(ind + bul + ' lia.')
                else:
                    out.append(ind + bul + ' idtac.')
                    out.extend(self.node(b0, ind + '  ', depth + 1, progress))
                out.append(ind + bul + ' idtac.')
                out.extend(self.node(b1, ind + '  ', depth + 1, progress))
                return out
        out.append(ind + 'finish_norm.')
        return out


def rule_lemma(name, start, target, tree, gen, progress=True, positive=(), bounds=None):
    lines = gen.node(tree, '  ', 0, progress)
    cnts, vs = coqgen.free_vars(start, target)
    bounds = bounds or {}
    binders = ' '.join(cnts + vs + [('(Hpos_%s : %d <= %s)' % (v, bounds[v], v)) if v in bounds else ('(Hpos_%s : 0 < %s)' % (v, v))
                                    for v in sorted(positive)])
    stmt = '%s %s %s' % (cfg_coq(start), '-->+' if progress else '-->*', cfg_coq(target))
    if binders:
        stmt = 'forall %s, %s' % (binders, stmt)
    return 'Lemma %s : %s.\nProof.\n  intros.\n%s\nQed.\n' % (name, stmt, NL.join(lines))


# ------------------------------------------------------------------------------------------------ validation
def check_stage(a, b, trials=3, maxv=6, seed=1):
    """concrete check: from a (random values) the literal machine passes through b."""
    rnd = random.Random(seed)
    vs = sorted(vars_of(a) | vars_of(b))
    for _ in range(trials):
        vals = {v: rnd.randint(0, maxv) for v in vs}
        if validate.reaches(a, b, vals) is None:
            return vals
    return None


def debug_loop(S, depth=2, width=700):
    """Print what the loop search does at S (for diagnosing 'generalised round fails')."""
    for S2, v, use in absorb_variants(S):
        print('variant on %s (use %s)' % (v, use))
        v2 = fresh(v)
        P = subst(S2, v, ((v2, 1),), 1)
        S1 = subst(S2, v, ((v2, 1),), 0)
        ops, C, how = run_stuck(P)
        m = match_shift_multi(S1, C) if how == 'stuck' else None
        print('  first round part: %s, %d steps; inserts %s' % (how, sum(o[1] for o in ops if o[0] == 'steps'), m))
        if not m:
            print('  C =', show(C)[:width])
            continue
        X, vg, ivs = generalize(S2, v, m)
        print('  X =', show(X)[:width])
        vg2 = fresh(vg)
        Xp = subst(X, vg, ((vg2, 1),), 1)
        Xt = subst(X, vg, ((vg2, 1),), 0)
        for iv in ivs:
            Xt = subst(Xt, iv, ((iv, 1),), 1)
        print('  Xt=', show(Xt)[:width])
        cfg = Xp
        for k in range(8):
            ops, cfg, how = run_stuck(cfg, Xt)
            print('   part %d: %s %d steps | %s' % (k, how, sum(o[1] for o in ops if o[0] == 'steps'), show(cfg)[:width]))
            if how != 'stuck':
                break
            lp = find_loop(cfg, depth - 1)
            print('     inner loop:', lp and (lp.v_at, lp.use_arg()))
            if lp is None:
                break
            cfg = lp.after()
