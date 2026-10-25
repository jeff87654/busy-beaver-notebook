"""Symbolic execution with automatic loop acceleration, for generating busycoq proofs of digit-list rules.

planner8.drive (exact symbolic execution on tapes with runs blk^n) stops ("STUCK") when the head meets a run it
cannot cross as a whole. In the hand-written proofs (bb8_048631_1RB0RG1LC1RE/gen048.py, bb8_240161_.../gen240.py)
a person then stated a loop lemma ("each round eats one block of this run and pushes a block onto a stack") and
proved it by induction. This module finds such loops itself:

  at a stuck configuration S, for a variable v of the run under the head (or of the run blocking the crossing):
    peel one copy of every run whose count contains v (v -> v' + 1) and execute on;
    if execution returns to S with v replaced by v' and one block g inserted at a fixed place on each side
    (a stack growing by one block per round), that is a loop:  S(v = j) -->* S(v = 0) + g^j at that place.
  otherwise split cases v = 0 / v = v' + 1 and explore both.

explore(start, target) returns a proof tree (nested dicts) that reaches the target on every branch, or raises.
Coq generation from the tree is in coqgen.py.
"""
import itertools
import planner8 as pl
from planner8 import BLANK, lin, lin_add, is_run, is_term, norm_side, show, canon, expand_side, Stuck, Halted

FRESH = itertools.count()


def fresh(base):
    return '%s%d' % (base.rstrip('0123456789'), next(FRESH))


# ------------------------------------------------------------------ substitution on configurations
def subst_side(side, v, form, const):
    """Replace variable v by (form + const) in every run count of the side. form: lin tuple, const >= 0."""
    out = []
    for t in side:
        if is_run(t):
            _, blk, cnt = t
            d = dict(cnt)
            if v in d:
                c = d.pop(v)
                newcnt = lin_add(lin(d), form, c)
                out.extend(list(blk) * (c * const))
                if newcnt:
                    out.append(('run', blk, newcnt))
                continue
        out.append(t)
    return norm_side(out)


def subst(cfg, v, form=(), const=0):
    q, L, R, mode = cfg
    return (q, subst_side(L, v, form, const), subst_side(R, v, form, const), mode)


def vars_of(cfg):
    q, L, R, mode = cfg
    vs = set()
    for side in (L, R):
        for t in side:
            if is_run(t):
                vs.update(k for k, _ in t[2])
    return vs


def coeff_ok(cfg, v):
    """v must appear with coefficient 1 wherever it appears (peeling then removes one block per run)."""
    q, L, R, mode = cfg
    for side in (L, R):
        for t in side:
            if is_run(t):
                for k, c in t[2]:
                    if k == v and c != 1:
                        return False
    return True


# ------------------------------------------------------------------ matching "the same configuration, one round later"
def side_tokens(side):
    return list(expand_side(side))


def match_side(s, c):
    """s, c: canonical token lists. Return None if c is not s with one concrete block inserted somewhere,
    else (position in s, inserted tuple) (inserted may be empty)."""
    n, m = len(s), len(c)
    if m < n:
        return None
    p = 0
    while p < n and p < m and s[p] == c[p]:
        p += 1
    q = 0
    while q < n - p and q < m - p and s[n - 1 - q] == c[m - 1 - q]:
        q += 1
    if p + q != n:
        return None
    mid = c[p:m - q]
    if not all(isinstance(t, int) for t in mid):
        return None
    return p, tuple(mid)


def match_shift(S1, C):
    """S1 = S with v -> v'. Same state/mode; each side differs by at most one inserted concrete block."""
    if S1[0] != C[0] or S1[3] != C[3]:
        return None
    ins = []
    for i in (1, 2):
        r = match_side(side_tokens(S1[i]), side_tokens(C[i]))
        if r is None:
            return None
        ins.append(r)
    return ins


# ------------------------------------------------------------------ exploration
class Fail(Exception):
    pass


def equiv(cfg, target, trials=4):
    """Same configuration as target? Compared on concrete tapes for a few random values of the variables
    (robust against the different ways the same tape can be written with runs)."""
    if cfg[0] != target[0] or cfg[3] != target[3]:
        return False
    import random
    import validate
    vs = sorted(vars_of(cfg) | vars_of(target))
    rnd = random.Random(12345)
    for _ in range(trials):
        vals = {v: rnd.randint(0, 5) for v in vs}
        if not validate.same(validate.concretize(cfg, vals), validate.concretize(target, vals)):
            return False
    return True


def run_until_stuck(cfg, target_canon, budget=200000, target=None):
    """Literal steps, crossings and aligns (planner8 primitives) until the target, a halt, or a stuck point."""
    ops, n = [], 0
    while True:
        if target is not None and cfg[0] == target[0] and equiv(cfg, target):
            ops.append(('steps', n))
            return ops, cfg, 'target'
        if target_canon is not None and canon(cfg) == target_canon:
            ops.append(('steps', n))
            return ops, cfg, 'target'
        try:
            pl.head(cfg)
        except Stuck:
            ops.append(('steps', n)); n = 0
            r, why = pl.try_crossing(cfg)
            if r:
                cfg2, lname = r
                run = cfg[2][0] if cfg[3] == '>' else cfg[1][0]
                ops.append(('cross', lname, pl.pieces(run[2])))
                cfg = cfg2
                continue
            a = pl.try_align(cfg)
            if a:
                cfg2, aname = a
                ops.append(('align', aname))
                cfg = cfg2
                continue
            # canonical (aligned) form, the same one the Coq side reaches with align_tape in finish_norm
            q, L, R, mode = cfg
            return ops, (q, norm_side(expand_side(L)), norm_side(expand_side(R)), mode), 'stuck'
        try:
            cfg = pl.step(cfg)
        except Halted:
            ops.append(('steps', n))
            return ops, cfg, 'halt'
        n += 1
        if n > budget:
            raise Fail('literal step budget')


def candidates(cfg, behind_first=False):
    """Loop/split variables to try at a stuck configuration: the run under the head first, then the run behind
    (the other way round when the crossing failed for lack of context behind the head)."""
    q, L, R, mode = cfg
    front, behind = (R, L) if mode == '>' else (L, R)
    order = []
    for side in ((behind, front) if behind_first else (front, behind)):
        for t in side:
            if is_run(t):
                for k, _ in t[2]:
                    if k not in order:
                        order.append(k)
                break
            if is_term(t):
                break
    return order


def try_loop(S, v, depth):
    """One round from S with v peeled; returns a loop record or None."""
    if not coeff_ok(S, v):
        return None
    v2 = fresh(v)
    P = subst(S, v, (( v2, 1),), 1)
    S1 = subst(S, v, ((v2, 1),), 0)
    try:
        ops, C, how = run_until_stuck(P, None)
    except (Fail, RuntimeError):
        return None
    if sum(o[1] for o in ops if o[0] == 'steps') == 0 or canon(C) == canon(P):
        return None                      # no progress: not a round
    # allow nested acceleration once inside a round
    rounds = [('ops', ops)]
    for _ in range(4):
        if how != 'stuck':
            return None
        m = match_shift(S1, C)
        if m is not None and any(ins for _, ins in m):
            return dict(v=v, v2=v2, start=S, peeled=P, after=C, round=rounds, inserts=m)
        if depth <= 0:
            return None
        sub = accelerate(C, depth - 1)
        if sub is None:
            return None
        rounds.append(('loop', sub))
        try:
            ops, C, how = run_until_stuck(sub['result'], None)
        except (Fail, RuntimeError):
            return None
        rounds.append(('ops', ops))
    return None


def accelerate(S, depth=1):
    """Find a loop at stuck configuration S. The record gets 'resultB': the configuration after all rounds but
    the last when v = v2 + 1 (v2 rounds, one copy of each v-run left), so that the last round is executed step by
    step (the target may lie inside it)."""
    for v in candidates(S):
        lp = try_loop(S, v, depth)
        if lp is None:
            continue
        v2 = lp['v2']
        S1 = subst(S, v, ((v2, 1),), 0)
        sides = []
        for i in (1, 2):
            toks = side_tokens(S1[i])
            # counts of the v-runs become the placeholder REM (what is left after the rounds); then insert g^v2
            toks = [('run', t[1], tuple(('_REM', c) if k == v2 else (k, c) for k, c in t[2])) if is_run(t) else t
                    for t in toks]
            pos, ins = lp['inserts'][i - 1]
            if ins:
                toks = toks[:pos] + [('run', ins, ((v2, 1),))] + toks[pos:]
            sides.append(norm_side(toks))
        cfg = (S1[0], sides[0], sides[1], S1[3])
        lp['resultB'] = subst(cfg, '_REM', (), 1)        # one block of each v-run left: the last round
        return lp
    return None


def explore(start, target, depth=2, splits=4, path='root'):
    """Proof tree reaching target from start on every branch."""
    tc = canon(target)
    node = {'start': start, 'target': target, 'items': [], 'path': path}
    cfg = start
    for _ in range(40):
        # A branch v = 0 restarts from the beginning of this stage: the target can be passed while the symbolic run
        # still carries v (the configurations agree with the target only when v = 0), before the stuck point.
        stage_start = cfg
        ops, cfg, how = run_until_stuck(cfg, tc, target=target)
        node['items'].append(('ops', ops, stage_start, cfg))
        if how == 'target':
            node['end'] = cfg
            return node
        if how == 'halt':
            raise Fail('halted at %s' % show(cfg))
        lp = accelerate(cfg, depth - 1)
        if lp is not None:
            v, v2 = lp['v'], lp['v2']
            # v = 0: no round at all;  v = v2 + 1: v2 rounds by the loop lemma, then the last round step by step
            b0 = explore(subst(stage_start, v, (), 0), subst(target, v, (), 0), depth, splits, path + '/%s=0' % v)
            b1 = explore(lp['resultB'], subst(target, v, ((v2, 1),), 1), depth, splits, path + '/%s=S%s' % (v, v2))
            node['items'].append(('loop', lp, b0, b1))
            return node
        if splits <= 0:
            raise Fail('stuck without loop at %s' % show(cfg))
        _, why = pl.try_crossing(cfg)
        cand = candidates(cfg, behind_first=bool(why) and why.startswith('left known region'))
        if not cand:
            raise Fail('stuck, no variable at %s' % show(cfg))
        v = cand[0]
        v2 = fresh(v)
        b0 = explore(subst(stage_start, v, (), 0), subst(target, v, (), 0), depth, splits - 1, path + '/%s=0' % v)
        b1 = explore(subst(stage_start, v, ((v2, 1),), 1), subst(target, v, ((v2, 1),), 1), depth, splits - 1,
                     path + '/%s=S%s' % (v, v2))
        node['items'].append(('split', v, v2, b0, b1))
        return node
    raise Fail('too many stages')


def describe(node, ind=''):
    out = []
    out.append(ind + 'from: ' + show(node['start']))
    for it in node['items']:
        if it[0] == 'ops':
            out.append(ind + '  ops: ' + ' '.join(o[0] if o[0] != 'steps' else 's%d' % o[1] for o in it[1]))
        elif it[0] == 'loop':
            lp = it[1]
            out.append(ind + '  LOOP on %s, inserts %s' % (lp['v'], lp['inserts']))
            out.append(ind + '     start : ' + show(lp['start']))
            out.append(ind + '     after all rounds but the last: ' + show(lp['resultB']))
            out.extend(describe(it[2], ind + '    '))
            out.extend(describe(it[3], ind + '    '))
        elif it[0] == 'split':
            out.append(ind + '  SPLIT %s' % it[1])
            out.extend(describe(it[3], ind + '    '))
            out.extend(describe(it[4], ind + '    '))
    if 'end' in node:
        out.append(ind + 'reached: ' + show(node['end']))
    return out
