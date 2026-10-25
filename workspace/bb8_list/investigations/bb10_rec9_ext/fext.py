"""Extension follower for 10-state extensions of the BB(9) record through its halting slot I1.

Every extension runs exactly like the record up to the record's D2-stage input (the event configuration after the
first full cycle; follow3.py --blank prints it as stage 2):
    D(0)^2 D(4) D(21) D(4) D(2) D(1)^(4 R1 - 19) D(1) D(R2) | tail (t = 6),  state A at the right end
    (the follower's canonical phase in blank mode; it is one step before Coq's Kt form, checked by chk_d2g.py),
with R1 = the first-exhaustion accumulator (3B+2, 2B+4 = 2^^13 3; omega-level 0) and R2 = the accumulator after the
first full cycle (omega-level 1).  This follower starts there (stages 0-1 are the record's own) and adds to follow3:
  * a cross-stage cache of fitted stage results (keyed by the canonical stage input and the parameters' residue classes);
  * meta-loop detection: the stage input repeats with period p (1..4) up to (i) fields shifted by constants and
    (ii) accumulator parameters replaced by new ones.
      - no decreasing field: an exact loop -> NONHALT (LOOP), after two full periods;
      - a decreasing field with a huge value (a unary counter): the counter becomes a parameter Z, the p stages are
        replayed on the template (cached fits), the accumulators' residues are iterated until they cycle, and the run
        jumps to the end of the counter (Z small and exact, accumulators huge with the cycled residues).  The loop is
        re-checked literally at small exact Z before the jump is accepted.
Usage: python fext.py MACHINE [--stages 40] [--budget 200000000] [--log FILE] [--verbose]
Prints "RESULT ..." at the end: HALT (with ones and the omega-level), NONHALT-LOOP, or UNCLEAR-*.
"""
from __future__ import annotations

import argparse
import math
import re
from fractions import Fraction
from pathlib import Path

import follow3 as F
from follow3 import Aff, A, Fail, Stage, jump, rule_check, fmt_sym, shape_of, fields_of, params_in, rebuild
from numres import Num, tau
from cend import c_end

HERE = Path(__file__).resolve().parent
LEVEL = F.LEVEL
F.RANK_LB.update({100 + i: 200 + 61 * i for i in range(60)})
ZMIN = 14          # the counter is left at a small exact value >= ZMIN after an acceleration
MAXIT = 40         # replay iterations for the residue cycle
FORCE_PERIODS = (25, 125)
NO_RETRY = [False]  # --no-retry: do not try other canonical states after a T (K-moments here are canonical in A)


def cend_input():
    """the record's halting configuration c_end(q, r) with 5q + 11 = 4 R1 - 19 and r = R2 - 5 (special stage input)"""
    return [('C', 'q', Aff(-6, {'R1': Fraction(4, 5)})), ('C', 'r', Aff(-5, {'R2': 1}))]


class CendStage(Stage):
    """literal stage from c_end(q, r): the tape is built by cend.c_end (parsed from the Coq definition), head in the
    middle (hyb10 dump format), state I reading 1; K-moments are detected in the canonical state A"""

    def run_at(self, vals, budget=None):
        budget = budget or self.budget
        key = (self.q,) + tuple(sorted(vals.items()))
        c = self.cache.get(key)
        if c is None or (c['kind'] == 'T' and c['step'] < budget):
            d = {p: A(cc).at(vals) for kind, p, cc in self.sym}
            tape, head, st = c_end(d['q'], d['r'])
            out = F.run_hyb(self.machine, f'{st} {head}' + chr(10) + tape, budget, start=st, canon=self.q)
            out['q'] = self.q
            if self.verbose:
                self.log(f'    run {vals}: {out["raw"][:200]}')
            self.cache[key] = out
        return self.cache[key]


def d2_input():
    one, two = A(1), A(2)
    return [('D', A(0), A(2)), ('D', A(4), one), ('D', A(21), one), ('D', A(4), one), ('D', A(2), one),
            ('D', one, Aff(-19, {'R1': 4})), ('D', one, one), ('D', Aff(0, {'R2': 1}), one),
            ('D', A(0), A(6)),
            ('B', (('R', ('1', one), one), ('R', ('0', two), one), ('D', A(0), A(5))), A(5)),
            ('R', ('1', one), one), ('R', ('0', two), one), ('R', ('1', one), one), ('R', ('0', two), one)]


# ----------------------------------------------------------------------------------------- symbolic helpers -----
def map_sym(sym, f):
    out = []
    for kind, p, c in sym:
        if kind == 'D':
            out.append(('D', f(p), f(c)))
        elif kind == 'J':
            out.append(('J', tuple((pat, f(k)) for pat, k in p), f(c)))
        elif kind == 'R':
            out.append(('R', (p[0], f(p[1])), f(c)))
        elif kind == 'B':
            out.append(('B', tuple(map_sym(p, f)), f(c)))
        else:
            out.append((kind, p, f(c)))
    return out


def ren_aff(a, ren, vals=None):
    a = A(a)
    vals = vals or {}
    c = a.c + sum(v * vals[k] for k, v in a.co.items() if k in vals)
    return Aff(c, {ren.get(k, k): v for k, v in a.co.items() if k not in vals})


def num_of(x, params):
    return A(x).num(params)


def plevel(a):
    return max([LEVEL.get(p, 0) for p in A(a).co] + [0])


def is_small_exact(n):
    return n.exact and n.x <= 20000


def canon(sym, params, ranks):
    """substitute exact small parameters, rename the rest R_1.. / Z_1.. in order of appearance"""
    vals = {p: params[p].x for p in params_in(sym) if is_small_exact(params[p])}
    order = []
    for f in fields_of(sym):
        for k in sorted(A(f).co):
            if k not in vals and k not in order:
                order.append(k)
    fwd = {}
    for i, k in enumerate(order):
        fwd[k] = (f'R_{i + 1}' if k.startswith('R') else f'Z_{i + 1}')
    back = {v: k for k, v in fwd.items()}
    csym = map_sym(sym, lambda a: ren_aff(a, fwd, vals))
    cparams = {fwd[k]: params[k] for k in order}
    # distinct sampling bases per parameter (follow2's equal bases made e.g. D(2 R2 - 4) and D(2 R3 - 4) coincide
    # at the base point and merge into one RLE item, which broke the fits)
    cranks = {fwd[k]: 100 + i for i, k in enumerate(order)}
    return csym, cparams, cranks, back


def unit_of(p, sym):
    u = 3 if p.startswith('R') else 1
    for x in F.all_affs(sym):
        if p in x.co:
            d = x.co[p].denominator
            for q in x.co:
                d = d * x.co[q].denominator // math.gcd(d, x.co[q].denominator)
            d = d * x.c.denominator // math.gcd(d, x.c.denominator)
            u = u * d // math.gcd(u, d)
    return u


def rename_res(res, back):
    out = dict(res)
    f = lambda a: ren_aff(a, back)
    for k in ('left', 'tail'):
        if k in res:
            out[k] = map_sym(res[k], f)
    if isinstance(res.get('ones'), Aff):
        out['ones'] = f(res['ones'])
    if isinstance(res.get('period'), dict):
        out['period'] = {back.get(p, p): v for p, v in res['period'].items()}
    return out


CACHE = {}
STATS = {'runs': 0, 'hits': 0}
CACHE_FILE = [None]          # per-machine pickle of CACHE (reruns reuse the fitted stages)


def save_cache():
    if CACHE_FILE[0]:
        import pickle
        tmp = CACHE_FILE[0].with_suffix('.tmp')
        tmp.write_bytes(pickle.dumps(CACHE))
        tmp.replace(CACHE_FILE[0])


def cached_stage(machine, sym, params, ranks, start, budget, log, verbose):
    csym, cparams, cranks, back = canon(sym, params, ranks)
    key = (start, fmt_sym(csym))
    for ent in CACHE.get(key, []):
        if all(cparams[p].known_mod(m) and cparams[p].m(m) == r for p, (m, r) in ent['cls'].items()):
            STATS['hits'] += 1
            res = rename_res(ent['res'], back)
            res['cls'] = {back[p]: v for p, v in ent['cls'].items()}
            return res
    STATS['runs'] += 1
    if csym and csym[0][0] == 'C':
        st = CendStage(machine, csym, cparams, cranks, budget, log, verbose, start=start)
    else:
        st = Stage(machine, csym, cparams, cranks, budget, log, verbose, start=start)
    st.no_retry = NO_RETRY[0]
    try:
        res = st.run()
    except Fail as ex:
        # outcome depends on deeper residues of one parameter (e.g. 5-adic digits of a zero count at a D2 stage):
        # force larger periods, sampled directly in the real class
        m = re.match(r'no period for (\w+)', str(ex))
        if not m:
            raise
        res = None
        for P in FORCE_PERIODS:
            st.force = {m.group(1): P}
            try:
                res = st.run()
                log(f'  (forced period {P} for {back.get(m.group(1), m.group(1))} after: {ex})')
                break
            except Fail as ex2:
                log(f'  (forced period {P} for {back.get(m.group(1), m.group(1))} failed: {ex2})')
        if res is None:
            raise
    res['q'] = st.q
    cls = {}
    if isinstance(res.get('period'), dict):
        for p, P in res['period'].items():
            m = P * unit_of(p, csym)
            cls[p] = (m, cparams[p].m(m))
    if res['kind'] in ('J', 'H') and res.get('period') is not None:
        CACHE.setdefault(key, []).append({'res': res, 'cls': cls})
        save_cache()
    out = rename_res(res, back)
    out['cls'] = {back[p]: v for p, v in cls.items()}
    return out


def advance(machine, sym, params, ranks, start, budget, log, verbose, quiet=False):
    """one stage: fitted literal stage, rule check, abstract jump"""
    res = cached_stage(machine, sym, params, ranks, start, budget, log, verbose)
    if res['kind'] != 'J':
        return {'kind': res['kind'], 'res': res}
    rc_ok, rc_seq = rule_check(machine, res['out']['tail_c'], res['e'], res['q'])
    if not rc_ok:
        return {'kind': 'RULES', 'res': res, 'rc': rc_seq}
    ev_sym, params2, info = jump(res['left'], res['tail'], params, res['e'])
    for p in params2:
        if p not in ranks:
            ranks[p] = min(4, max(ranks.values()) + 1)
    if not quiet:
        log(f'  champion phase (period {res["period"]}, e={res["e"]}): {fmt_sym(res["left"])} | tail {fmt_sym(res["tail"])}')
        newp = {k: str(v) for k, v in params2.items() if k not in params}
        log(f'  jump -> {info["event"]}, huge-length list cleared: {info["huge_depth"]}, level {info.get("level", 0)}, new {newp}')
    return {'kind': 'J', 'sym': ev_sym, 'params': params2, 'start': res['q'], 'info': info, 'res': res}


# ----------------------------------------------------------------------------------------- meta-loops -----------
def compare(sa, sb):
    """None, or (lin, ren): lin = {field: shift}, ren = {old param: new param}"""
    if shape_of(sa) != shape_of(sb):
        return None
    fa, fb = fields_of(sa), fields_of(sb)
    if len(fa) != len(fb):
        return None
    lin, ren = {}, {}
    for i, (x, y) in enumerate(zip(fa, fb)):
        x, y = A(x), A(y)
        if x == y:
            continue
        if x.co == y.co and x.co:          # a constant field (no parameters) must not change
            lin[i] = y.c - x.c
            continue
        if len(x.co) == 1 and len(y.co) == 1 and x.c == y.c:
            (kx, vx), = x.co.items()
            (ky, vy), = y.co.items()
            if vx == vy and kx != ky and ren.get(kx, ky) == ky:
                ren[kx] = ky
                continue
        return None
    return lin, ren


class Accel(Exception):
    pass


def accelerate(machine, sym, params, ranks, start, p, lin, ren0, budget, log, verbose):
    """sym (current input) repeats the input p stages back with the shifts lin.  Returns (sym', params', start, note)
    or None when there is no huge decreasing field."""
    fields = fields_of(sym)
    dec = {i: d for i, d in lin.items() if d < 0}
    cand = [i for i in dec if not is_small_exact(num_of(fields[i], params))]
    if not cand:
        return None
    keyf = lambda i: (plevel(fields[i]), tuple(sorted(A(fields[i]).co.items())), A(fields[i]).c / (-dec[i]))
    cand.sort(key=keyf)
    if len(cand) > 1 and plevel(fields[cand[0]]) == plevel(fields[cand[1]]) and \
            set(A(fields[cand[0]]).co) == set(A(fields[cand[1]]).co) and A(fields[cand[0]]).co != A(fields[cand[1]]).co:
        raise Accel('two counters with incomparable values')
    i0 = cand[0]
    d0 = int(-dec[i0])
    if d0 != -dec[i0]:
        raise Accel(f'non-integer counter step {dec[i0]}')
    Fv = A(fields[i0])
    zname = f'Z{len([k for k in params if k.startswith("Z")]) + 1}'
    Zf = Aff(0, {zname: 1})
    newf = []
    for j, f in enumerate(fields):
        if j == i0:
            newf.append(Zf)
        elif j in lin:
            newf.append(A(f) + (Fv - Zf) * (Fraction(lin[j]) / d0))
        else:
            newf.append(f)
    tmpl = rebuild(shape_of(sym), newf)[0]
    cur = dict(params)
    cur[zname] = num_of(Fv, params)
    ranks[zname] = 2
    LEVEL[zname] = plevel(Fv)
    # the loop's accumulators: the parameters that the period renames (old name -> new name)
    accs = sorted(ren0.values())
    if any(a in Fv.co for a in accs):
        raise Accel('the counter involves a renamed accumulator')
    log(f'  META-LOOP period {p}: counter field {Fv} -> {zname} (step -{d0}); accumulators {accs}; template {fmt_sym(tmpl)}')
    seq, nums = [], []
    lev_before = max([LEVEL.get(a, 0) for a in accs] + [0])
    lev_inside = lev_before
    zmods = set()
    lam = None
    for it in range(MAXIT):
        s_sym, s_par, s_st = tmpl, cur, start
        for k in range(p):
            out = advance(machine, s_sym, s_par, ranks, s_st, budget, log, verbose, quiet=True)
            if out['kind'] != 'J':
                raise Accel(f'replay iteration {it} stage {k}: {out["kind"]}')
            for pp, (m, _) in out['res'].get('cls', {}).items():
                if pp == zname:
                    zmods.add(m)
            lev_inside = max(lev_inside, out['info'].get('level', 0))
            s_sym, s_par, s_st = out['sym'], out['params'], out['start']
        if s_st != start:
            raise Accel('replay ends in another canonical state')
        c = compare(tmpl, s_sym)
        if c is None:
            raise Accel(f'replay iteration {it}: the input shape changed: {fmt_sym(s_sym)}')
        l2, r2 = c
        if l2 != {i0: -d0}:
            raise Accel(f'replay iteration {it}: shifts {l2} (expected only the counter, -{d0})')
        if set(r2) != set(accs):
            raise Accel(f'replay iteration {it}: renamed {r2} vs accumulators {accs}')
        nxt = dict(cur)
        nxt[zname] = cur[zname] - d0
        for a in accs:
            nxt[a] = s_par[r2[a]]
        cur = nxt
        seq.append(tuple(str(cur[a]) for a in accs))
        nums.append({a: cur[a] for a in accs})
        if any(is_small_exact(cur[a]) for a in accs):
            continue
        for L in (1, 2, 3, 4, 6, 8, 12):
            if len(seq) >= 3 * L + 2 and all(seq[-1 - i] == seq[-1 - i - L] for i in range(2 * L)):
                lam = L
                break
        if lam:
            break
    if lam is None:
        raise Accel(f'accumulator residues did not cycle in {MAXIT} iterations: {seq[-3:]}')
    lam_z = 1
    for m in zmods:
        lz = m // math.gcd(m, d0)
        lam_z = lam_z * lz // math.gcd(lam_z, lz)
    lam_tot = lam * lam_z // math.gcd(lam, lam_z)
    M = d0 * lam_tot
    Z0 = num_of(Fv, params)
    if not Z0.known_mod(M):
        raise Accel(f'counter residue mod {M} unknown')
    zf = ZMIN + ((Z0.m(M) - ZMIN) % M)
    # N = (Z0 - zf)/d0 = 0 mod lam_tot; the replay index i (0-based, after i+1 iterations) with (i+1) = 0 mod lam
    n_idx = len(seq) - 1
    while (n_idx + 1) % lam:
        n_idx -= 1
    final = nums[n_idx]
    lev = max(lev_before, LEVEL[zname])
    note = ''
    if lev_inside > lev_before:
        note = 'OMEGA-STEP-PER-ITERATION'
    out_par = dict(params)
    ren = {}
    for a in accs:
        nm = f'R{len([k for k in out_par if k.startswith("R")]) + 1}'
        out_par[nm] = final[a]
        LEVEL[nm] = lev if not note else max(lev, lev_inside) + 1
        ranks[nm] = min(4, max(ranks.values()) + 1)
        ren[a] = nm
    new_sym = map_sym(tmpl, lambda a: ren_aff(a, ren, {zname: zf}))
    log(f'  META-LOOP accelerated: counter {Z0} -> {zf} (step {d0}, residue cycle {lam}, Z moduli {sorted(zmods)}); '
        f'accumulators {[(a, ren[a], str(out_par[ren[a]])) for a in accs]} level {LEVEL[ren[accs[0]]] if accs else lev} {note}')
    # literal re-check of the loop map at small exact counters zf + 2M -> zf + M -> zf
    for k in (2, 1):
        s_sym = map_sym(tmpl, lambda a: ren_aff(a, ren, {zname: zf + k * M}))
        s_par, s_st = dict(out_par), start
        for j in range(p * lam_tot):
            o = advance(machine, s_sym, s_par, ranks, s_st, budget, log, verbose, quiet=True)
            if o['kind'] != 'J':
                raise Accel(f'small-counter check at Z={zf + k * M}: {o["kind"]}')
            s_sym, s_par, s_st = o['sym'], o['params'], o['start']
        exp = map_sym(tmpl, lambda a: ren_aff(a, ren, {zname: zf + (k - 1) * M}))
        c = compare(exp, s_sym)
        if c is None or c[0]:
            raise Accel(f'small-counter check at Z={zf + k * M} failed: got {fmt_sym(s_sym)}')
    log(f'  META-LOOP small-counter check passed (Z = {zf + 2 * M} -> {zf + M} -> {zf}, literal fits)')
    return new_sym, out_par, start, note


# ----------------------------------------------------------------------------------------- driver ---------------
def follow_ext(machine, stages=40, budget=200_000_000, log=print, verbose=False, from_d2=False):
    t = tau()
    params = {'R1': t, 'R2': t}
    ranks = {'R1': 2, 'R2': 3}
    LEVEL.clear()
    LEVEL.update({'R1': 0, 'R2': 1})
    # blank-mode K-moments are canonical in state A (the stage-1 output phase); c_end skips the common D2 stage
    sym, start = (d2_input() if from_d2 else cend_input()), 'A'
    hist = []
    notes = []
    events = []
    for s in range(stages):
        log(f'stage {s}: input {fmt_sym(sym)}')
        for p in (1, 2, 3, 4):
            if len(hist) < p:
                break
            c = compare(hist[-p][0], sym) if hist[-p][2] == start else None
            if c is None:
                continue
            lin, ren = c
            if not any(d < 0 for d in lin.values()):
                if len(hist) >= 2 * p and hist[-2 * p][2] == start and compare(hist[-2 * p][0], hist[-p][0]) is not None:
                    log(f'  LOOP (period {p}) without a decreasing field: shifts {lin}, renamed {ren}')
                    return {'result': 'NONHALT-LOOP', 'stages': s, 'events': events, 'notes': notes}
                continue
            try:
                acc = accelerate(machine, sym, params, ranks, start, p, lin, ren, budget, log, verbose)
            except Accel as ex:
                log(f'  META-LOOP not accelerated: {ex}')
                notes.append(f'accel-fail:{ex}'[:120])
                acc = None
            if acc:
                sym, params, start, note = acc
                notes.append('accel' + (':' + note if note else ''))
                events.append('M')
                hist = []
                log(f'stage {s}: input after the meta-loop {fmt_sym(sym)}')
            break
        hist.append((sym, dict(params), start))
        out = advance(machine, sym, params, ranks, start, budget, log, verbose)
        if out['kind'] == 'H':
            res = out['res']
            ones = res['ones']
            lev = plevel(ones) if isinstance(ones, Aff) else None
            log(f'  HALT: ones = {ones}, state {res["halt_state"]}, omega-level {lev}')
            return {'result': 'HALT', 'stages': s + 1, 'ones': ones, 'level': lev, 'events': events, 'notes': notes}
        if out['kind'] != 'J':
            o = out['res'].get('out', {})
            log(f'  outcome {out["kind"]}: {str(o.get("raw", ""))[:300]}')
            return {'result': 'UNCLEAR-' + out['kind'], 'stages': s + 1, 'events': events, 'notes': notes}
        sym, params, start = out['sym'], out['params'], out['start']
        events.append(('F' if out['info']['huge_depth'] else '') + out['info']['event'][0] + str(out['info'].get('level', 0)))
    return {'result': 'MAXSTAGES', 'stages': stages, 'events': events, 'notes': notes}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('machine')
    ap.add_argument('--stages', type=int, default=40)
    ap.add_argument('--budget', type=int, default=200_000_000)
    ap.add_argument('--log')
    ap.add_argument('--verbose', action='store_true')
    ap.add_argument('--from-d2', action='store_true', help='start at the D2-stage input instead of c_end')
    ap.add_argument('--no-retry', action='store_true', help='no other canonical states after a T outcome')
    a = ap.parse_args()
    NO_RETRY[0] = a.no_retry
    lf = open(a.log, 'w') if a.log else None

    def log(s):
        print(s, flush=True)
        if lf:
            lf.write(s + '\n')
            lf.flush()

    log(f'machine {a.machine} (from ' + ('the record D2-stage input)' if a.from_d2 else 'c_end)'))
    import pickle
    CACHE_FILE[0] = HERE / 'logs' / f'cache_{a.machine}{"_d2" if a.from_d2 else ""}.pkl'
    if CACHE_FILE[0].exists():
        CACHE.update(pickle.loads(CACHE_FILE[0].read_bytes()))
        log(f'(loaded {sum(len(v) for v in CACHE.values())} cached stage fits)')
    try:
        r = follow_ext(a.machine, a.stages, a.budget, log, a.verbose, a.from_d2)
        lv = max(LEVEL.values(), default=0)
        log(f'RESULT {r["result"]} stages={r["stages"]} maxlevel={lv} events={" ".join(map(str, r["events"]))} '
            f'notes={r["notes"]}' + (f' ones={r["ones"]} ones_level={r["level"]}' if 'ones' in r else '') +
            f' stage_runs={STATS["runs"]} cache_hits={STATS["hits"]}')
    except (Fail, AssertionError, RuntimeError, KeyError, ZeroDivisionError) as ex:
        log(f'RESULT FAIL {type(ex).__name__}: {ex} stage_runs={STATS["runs"]}')


if __name__ == '__main__':
    main()
