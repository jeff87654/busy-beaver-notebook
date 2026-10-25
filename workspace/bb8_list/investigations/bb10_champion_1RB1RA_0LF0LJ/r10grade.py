"""r10grade.py: grade machines of the BB(10) champion's subtree against the champion
    1RB1RA_0LC0LF_0RD1LC_1RA1RG_1RZ0RA_1LB1LF_1LH1RE_0LI1LH_0LF0LJ_1LH0LJ   (Racheline 2024, sigma > f_omega^2(25))

usage:  python r10grade.py MACHINE [-v]                 one machine (verbose with -v)
        python r10grade.py --list FILE [OUT.tsv]         one TSV line per machine (BEATS rows also to stdout)
        env R10_LIT_STEPS (literal run length, default 2e7), R10_KBITS (residue bits, default 16)

Family (see ../bb10_champion_1RB1RA_0LF0LJ.md):  Kd ds a b = 0^inf [D on 0] 1^(b+1) 0 1^a 0 1^d1 0 1^d2 ... 0^inf.
Rules R1-R3 are the BB(9) champion's (proved in Coq for it):  R1 a+1 -> a, b+3;  R2 top digit y+1 -> y, a = b+2, b = 1;
R3 k >= 1 leading zero digits, 2k <= b: refill  [2^(k-1), b+2-2k, y, ...], a = 2, b = 1.  R4 (the used-up list Kd [] 0 b)
is machine specific; the grader fits it (r4fit.py) and validates the fit on a disjoint window.

Stages
 1. parse (fails loudly); short literal run (3e5 steps) for a quick rejection;
 2. literal run from the blank tape with kdtrace.exe (R1 checked inside, every R2/R3 transition checked here);
    R1-R3 literal grid (BB(9) predictions); R4 fit (b = 16..79) validated on b = 80..143 and on the literal R4 events;
 3. abstract continuation (exact integers while small, residues mod 2^K when huge; hlev.py): clears the current list,
    applies R4, detects halting classes and cycles of the residue dynamics; exact counters too small for an R3 site
    (boundary region) are handled by a literal step;
 4. key = (R_huge, ell, v, slope): score ~ f_omega^R_huge(f_ell(..)); ell-1 = depth of the deepest digit (value v) of the
    last exact rebuilt list, slope = depth of the next rebuilt list per unit of b.  Champion (1, 25, 2, 3/4), i.e.
    sigma ~ f_omega(f_25^2(..)) > f_omega^2(25).  Grades: BEATS-CHAMPION? / EQUAL / EQUAL-KEY / BELOW / NONHALT-PREDICTED /
    HALTS-EARLY / OTHER-STRUCTURE / R4-UNFIT (R1-R3 hold, R4 fits no template: inspect) / UNRESOLVED.
"""
import os
import re
import subprocess
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from kd import run_next, CH10                      # noqa: E402
from rules import pred                              # noqa: E402
import r4fit                                        # noqa: E402
import hlev                                         # noqa: E402
from modexact import Huge                           # noqa: E402

KDTRACE = os.path.join(HERE, 'kdtrace.exe')
LIT_STEPS = int(os.environ.get('R10_LIT_STEPS', '20000000'))
CHAMP_KEY = (2, 25, 2, F(3, 4))     # (k, x, v, slope): sigma ~ f_omega^k(x), champion f_omega^2(25)
# k = number of f_omega applications = deep clearings (the first, of the exact rebuilt list, counts when its deepest
# digit is at depth >= 3, i.e. it is cleared at level x = ell >= 4); x = ell = 1 + depth of that list's deepest digit
# (the first clearing is ~ f_x^v(..) ~ f_omega(x)); v = that digit; slope = depth of the next rebuilt list per unit of b.
KBITS = int(os.environ.get('R10_KBITS', '16'))

TRANS = re.compile(r'^([01][LR][A-Z]|---)$')


def parse_machine(M):
    rows = M.split('_')
    n = len(rows)
    if n < 2 or n > 16 or any(len(r) != 6 for r in rows):
        raise ValueError('bad machine string %r' % M)
    for r in rows:
        for t in (r[:3], r[3:]):
            if not TRANS.match(t):
                raise ValueError('bad transition %r in %r' % (t, M))
            if t != '---' and t[2] != 'Z' and ord(t[2]) - 65 >= n:
                raise ValueError('transition %r targets a missing state in %r' % (t, M))
    return n


# ---------------------------------------------------------------- stage 1: rule grid
def grid_cases():
    import itertools
    for n in range(0, 4):
        for ds in itertools.product(range(0, 4), repeat=n):
            if ds and ds[-1] == 0:
                continue
            for a in range(0, 3):
                for b in range(0, 9):
                    yield ds, a, b
    for k in range(1, 9):                     # deeper R3 sites with the champion's (0,0,3) blocks
        for v in (1, 3):
            for b in range(2 * k, 2 * k + 5):
                yield (0,) * k + (v, 0, 0, 3), 0, b




def rule_kind(ds, a):
    if a:
        return 'R1e' if not any(ds) else 'R1'
    return 'R2' if ds and ds[0] else 'R3'


def r123_check(M, verbose=False):
    """Literal check of R1 (non-empty list), R2, R3 on the grid; R1 on the empty list ('R1e', used by start-ups only)
    is checked separately.  returns (ok, n_checked, first_failure, r1e_failure)"""
    n = 0
    r1e = None
    for ds, a, b in grid_cases():
        if a == 0 and all(d == 0 for d in ds):
            continue                           # R4: machine specific
        p = pred(ds, a, b, r4=lambda bb: None)
        if p is None or p[0] != 'K':
            continue                           # boundary region / halting boundary: not part of the family rules
        kind = rule_kind(ds, a)
        if kind == 'R1e' and r1e is not None:
            continue
        r = run_next(M, ds, a, b, N=20000)
        n += 1
        if not (r[0] == 'K' and r[2] == p[1]):
            why = '%s fails at Kd %s %d %d: predicted %s, got %s' % (kind, list(ds), a, b, p[1], r[:3])
            if kind == 'R1e':
                r1e = why
                continue
            return False, n, why, r1e
    return True, n, None, r1e


# ---------------------------------------------------------------- stage 2: literal run
def literal_run(M, steps):
    out = subprocess.run([KDTRACE, M, str(steps)], capture_output=True, text=True, timeout=3600)
    lines = out.stdout.splitlines()
    if not lines:
        raise RuntimeError('kdtrace produced no output: %s' % out.stderr)
    return lines


def quick_reject_py(M, steps=20000):
    """in-process literal run (no subprocess): reason if an early Kd transition leaves R1-R3, else None"""
    from kd import Sim, parse_at
    s = Sim(M, size=1 << 15)
    prev = None
    while s.steps < steps:
        if not s.step():
            return None                       # halts early: let the full stage report it
        if s.state != 3:
            continue
        cur = parse_at(s)
        if cur is None:
            continue
        if prev is not None:
            if prev[1] >= 1:
                ok = cur == (prev[0], prev[1] - 1, prev[2] + 3)
                if not ok:
                    return 'literal run: R1 fails at step %d: %s -> %s' % (s.steps, prev, cur)
            elif any(prev[0]):
                pr = pred(*prev, r4=lambda bb: None)
                if pr is not None and (pr[0] != 'K' or pr[1] != cur):
                    return 'literal run leaves R2/R3 at step %d: from %s predicted %s got %s' % (s.steps, prev, pr, cur)
        prev = cur
    return None


# transitions used by R1-R3 (usage_r123.py); a machine that agrees with the champion on all of them has the
# champion's R1-R3 behaviour verbatim (the BB(9)-champion Coq phases read nothing else)
R123_TRANS = ['A0', 'A1', 'B0', 'B1', 'C0', 'C1', 'D0', 'D1', 'E1', 'F0', 'F1', 'G1']


def same_r123(M):
    def tr(m, t):
        q = ord(t[0]) - 65
        return m.split('_')[q][3 * int(t[1]):3 * int(t[1]) + 3]
    return all(tr(M, t) == tr(CH10, t) for t in R123_TRANS)


def quick_reject(M, steps=300000):
    """short literal run: reason string if R1 or an R2/R3 transition already deviates from the family, else None"""
    why = quick_reject_py(M)
    if why:
        return why
    lines = literal_run(M, steps)
    prev = None
    for l in lines:
        f = l.split()
        if f[0] == 'R1FAIL':
            return 'literal run: ' + l
        if f[0] != 'K':
            continue
        ds = tuple(int(x) for x in f[4].split(',')) if len(f) > 4 else ()
        cur = (ds, int(f[2]), int(f[3]))
        if prev is not None and prev[1] == 0 and any(prev[0]):
            pr = pred(*prev, r4=lambda bb: None)
            if pr is not None and (pr[0] != 'K' or pr[1] != cur):
                return 'literal run leaves R2/R3 at step %s: from %s predicted %s got %s' % (f[1], prev, pr, cur)
        prev = cur
    if prev is None and lines[-1].startswith('TIMEOUT'):
        return 'no Kd configuration within %d steps' % steps
    return None


def r4_apply(p, rules, outs, b):
    """R4 outcome for an exact counter b: literal probe if available, else the fitted rule."""
    if b in outs:
        o = outs[b]
        if o[0] == 'K':
            return ('K', (o[1], o[2], o[3]))
        if o[0] == 'HALT':
            return ('HALT', o[1])
        return ('TIMEOUT',)
    r = b % p
    n = (b - r) // p
    pr = r4fit.rule_predict(rules[r], n)
    if pr[0] == 'HALT':
        return ('HALT', pr[1])
    return ('K', (pr[1], pr[2], pr[3]))


def deepest(ds):
    d = -1
    for i, v in enumerate(ds):
        if v:
            d = i
    return d


# ---------------------------------------------------------------- main grading

# ---------------------------------------------------------------- main grading
def grade(M, verbose=False, S=None):
    info = {'machine': M}

    def say(*a):
        if verbose:
            print(*a)

    try:
        parse_machine(M)
    except ValueError as e:
        return dict(info, grade='INVALID', note=str(e))
    # ------------------------------------------------ stage 2a: literal run from the blank tape (short run first)
    why = quick_reject(M)
    if why:
        return dict(info, grade='OTHER-STRUCTURE', note=why)
    lines = literal_run(M, LIT_STEPS)
    last = lines[-1].split()
    kconfs = [l.split() for l in lines if l.startswith('K ')]
    halted = last[0] == 'HALT'
    if halted:
        ones = int(last[4])
        info.update(grade='HALTS-EARLY', sigma=ones + 1,
                    note='halts at step %s (state %s reading %s), sigma = %d' % (last[1], last[2], last[3], ones + 1))
    if last[0] == 'R1FAIL':
        return dict(info, grade='OTHER-STRUCTURE', note='literal run: ' + lines[-1])
    if not kconfs:
        if halted:
            return info
        return dict(info, grade='OTHER-STRUCTURE', note='no Kd configuration within %d steps' % LIT_STEPS)
    if not halted and last[0] != 'TIMEOUT':
        return dict(info, grade='UNRESOLVED', note='unexpected kdtrace line ' + lines[-1])
    # ------------------------------------------------ stage 2b: every literal transition against the rules
    events = []          # exact rebuild events ('exact', b, list, step)
    r4seen = []
    notes = []
    prev = None
    for f in kconfs:
        step, a, b = int(f[1]), int(f[2]), int(f[3])
        ds = tuple(int(x) for x in f[4].split(',')) if len(f) > 4 else ()
        cur = (ds, a, b)
        if prev is not None and prev[1] == 0:
            if all(d == 0 for d in prev[0]):
                events.append(('exact', prev[2], cur[0], step))
                r4seen.append((prev[2], cur))
            else:
                pr = pred(*prev, r4=lambda bb: None)
                if pr is None:
                    notes.append('literal run passes the R3 boundary region at step %d (%s)' % (step, prev))
                elif pr[0] != 'K' or pr[1] != cur:
                    return dict(info, grade='OTHER-STRUCTURE',
                                note='literal run leaves R2/R3 at step %d: from %s predicted %s got %s' %
                                (step, prev, pr, cur))
        prev = cur
    info['events'] = events
    if halted:
        info['note'] += '; %d exact rebuilds before the halt' % len(events)
        return info
    say('literal run: %d Kd configurations to step %s follow R1-R4; rebuilds at exact b = %s' %
        (len(kconfs), last[1], [e[1] for e in events]))
    # ------------------------------------------------ stage 1a: rule grid
    ok, n, why, r1e = (True, 0, None, None) if same_r123(M) else r123_check(M)
    if not ok:
        return dict(info, grade='OTHER-STRUCTURE',
                    note='literal run follows the rules to step %s, but the grid fails: %s' % (last[1], why))
    say(('R1-R3 transitions identical to the champion (A0 A1 B0 B1 C0 C1 D0 D1 E1 F0 F1 G1): grid skipped' if n == 0 else
         'R1-R3 grid: %d configurations match the BB(9)-champion rules' % n) + ('' if not r1e else
                                                                          ' (R1 on the empty list fails: %s)' % r1e))
    if r1e:
        notes.append('R1 on the empty list fails (start-up only)')
    # ------------------------------------------------ stage 1b: R4 fit, checked against the literal R4 events (literal probes b = 0..143)
    p, rules, outs = r4fit.fit_r4(M)
    if p is not None:
        info['r4'] = '; '.join('b=%dn+%d: %s' % (p, r, r4fit.rule_str(rules[r])) for r in range(p))
        say('R4 fit (fitted on b = 16..79, validated on b = 80..143):', info['r4'])
    else:
        info['r4'] = 'FIT FAILED: ' + rules
        say('R4 fit failed:', rules)
    if p is None:
        return dict(info, grade='R4-UNFIT', note='R1-R3 hold (grid and literal run), R4 does not fit a template: ' + rules)
    for b0, cur in r4seen:
        pr = r4_apply(p, rules, outs, b0)
        if pr[0] != 'K' or pr[1] != cur:
            return dict(info, grade='OTHER-STRUCTURE', note='literal R4 at b=%d disagrees with the fit: '
                        'predicted %s got %s' % (b0, pr, cur))
    # ------------------------------------------------ stage 3: abstract continuation
    S = S or hlev.Setup(KBITS)
    return finish(info, S, prev, events, p, rules, outs, notes, say, M)


class Unresolved(Exception):
    pass

class HaltedInList(Exception):
    pass


def clear_mixed(S, M, ds, b, notes, say=lambda *a: None):
    """Clear an explicit list from counter b with the clearing functions; whenever an EXACT counter is too small for
    the next R3 site (2j > b, the boundary region) and a machine M is given, take one literal step from that Kd
    configuration instead (cheap: all values are small there) and continue with the configuration it reaches."""
    ds = list(ds)
    for _ in range(10000):
        j = 0
        while j < len(ds) and not (isinstance(ds[j], Huge) or ds[j] != 0):
            j += 1
        if j == len(ds):
            return b
        if not isinstance(b, Huge) and j >= 1 and 2 * j > b:
            if M is None or any(isinstance(x, Huge) for x in ds):
                raise ValueError('boundary region (2j > b) at depth %d, b=%d' % (j, b))
            r = run_next(M, tuple(ds), 0, b, N=10 ** 7)
            notes.append('boundary-region step at depth %d, b=%d -> %s' % (j, b, r[2] if r[0] == 'K' else r[:3]))
            say('   boundary region: Kd %s 0 %d -> %s' % (ds, b, r[:3]))
            if r[0] == 'HALT':
                raise HaltedInList('halts in the boundary region at b=%d (ones %d)' % (b, r[3].ones()))
            if r[0] != 'K':
                raise ValueError('boundary-region step from b=%d: %s' % (b, r[:2]))
            nds, na, nb = r[2]
            ds = list(nds)
            b = nb + 3 * na
            continue
        b = hlev.uiter_any(S, j, ds[j], b)
        ds[j] = 0
    raise ValueError('clear_mixed: too many steps')



def abstract_run(S, prev, events, p, rules, outs, say=lambda *a: None, M=None, notes=None):
    """Continue from the exact Kd configuration prev = (ds, a, b): clear the list, apply R4 (literal probes for exact
    counters, the fitted templates for huge ones), until a halting class or a repeated residue state.
    Returns (result, huge_events); appends exact rebuilds to events."""
    ds, a, b = prev
    b = b + 3 * a
    try:
        b = clear_mixed(S, M, list(ds), b, notes if notes is not None else [], say)
    except HaltedInList as e:
        return ('HALT', 'list', str(e)), []
    except (ValueError, hlev.PrecisionError) as e:
        raise Unresolved('continuation of the literal list: %s' % e)
    say('after the current list: b = %r' % (b,))
    huge_events = []
    seen = {}
    for it in range(200):
        if not isinstance(b, Huge):
            if b > 10 ** 6:
                raise Unresolved('exact counter %d too large for a literal R4' % b)
            pr = r4_apply(p, rules, outs, b)
            if pr[0] == 'HALT':
                return ('HALT', 'exact', b, pr[1]), huge_events
            if pr[0] == 'TIMEOUT':
                r2 = r4fit.probe_fast(M, b, b + 1, 0, 10 ** 7) if M else {b: ('TIMEOUT',)}
                if r2 is None:
                    rr = run_next(M, (), 0, b, N=10 ** 7)
                    r2 = {b: rr if rr[0] == 'TIMEOUT' else ('RETURN', rr[1])}
                if r2[b][0] != 'TIMEOUT':
                    raise Unresolved('R4 at exact b=%d returns only after many steps: %s' % (b, r2[b][:2]))
                return ('NORETURN', 'exact', b, None), huge_events
            if pr[0] != 'K':
                raise Unresolved('R4 at exact b=%d: %s' % (b, pr))
            nds, na, nb = pr[1]
            if na and not any(nds):
                raise Unresolved('R4 output with an empty list and a > 0 (R1e)')
            events.append(('exact', b, nds, None))
            say('R4 at exact b=%d -> Kd %s %d %d' % (b, list(nds), na, nb))
            try:
                b = clear_mixed(S, M, list(nds), nb + 3 * na, notes if notes is not None else [], say)
            except HaltedInList as e:
                return ('HALT', 'list', str(e)), huge_events
            except (ValueError, hlev.PrecisionError) as e:
                raise Unresolved('clearing an exact rebuilt list: %s' % e)
            say('   -> b = %r' % (b,))
            continue
        # class of b mod p: the 2-part from the residue mod 2^K; the 3-part from the fact that every value of a
        # clearing function is 1 mod 3 (U_0 x = 3x+7, and U_(j+1) x is a value of U_j), see the report section 4
        s2 = (p & -p).bit_length() - 1
        odd = p >> s2
        if odd not in (1, 3):
            raise Unresolved('R4 period %d not supported for huge counters' % p)
        r = b.r % (1 << s2) if odd == 1 else next(x for x in range(p) if x % (1 << s2) == b.r % (1 << s2) and x % 3 == 1)
        if b.r in seen:
            return ('CYCLE', seen[b.r], it), huge_events
        seen[b.r] = it
        rule = rules[r]
        if rule['kind'] == 'HALT':
            return ('HALT', 'huge', r, rule), huge_events
        if rule['kind'] == 'TIMEOUT':
            return ('NORETURN', 'huge', r, rule), huge_events
        nbits = S.K - s2
        n_r = ((b.r - r) % S.M) >> s2
        if odd == 3:
            n_r = (n_r * pow(3, -1, 1 << nbits)) % (1 << nbits)
        n = Huge(n_r % (1 << nbits))
        t = rule['list']
        if t['alpha'] == 0 and (rule['a'][0] or rule['b'][0]):
            if all_shallow(rules):
                return ('SHALLOWLOOP', 'huge', r, rule), huge_events
            raise Unresolved('shallow rebuild with a huge counter start: precision')
        na = hlev.lin_val(rule['a'], n, nbits)
        nb = hlev.lin_val(rule['b'], n, nbits)
        if isinstance(na, Huge) or isinstance(nb, Huge):
            ra = na.r if isinstance(na, Huge) else na
            rb = nb.r if isinstance(nb, Huge) else nb
            start = Huge((3 * ra + rb) % (1 << nbits))     # only the low nbits are meaningful (deep template)
        else:
            start = nb + 3 * na
        try:
            b2, inf = hlev.clear_template(S, t, n, nbits, start)
        except hlev.PrecisionError as e:
            if t['alpha'] == 0 and all_shallow(rules):
                return ('SHALLOWLOOP', 'huge', r, rule), huge_events
            raise Unresolved('clearing a huge template: %s' % e)
        except ValueError as e:
            raise Unresolved('clearing a huge template: %s' % e)
        slope = F(t['alpha'] * len(t['B']), p) if t['alpha'] else F(0)
        huge_events.append(('huge', r, r4fit.tmpl_str(t), slope, inf['deep']))
        say('R4 at huge b (class %d mod %d) -> Kd %s a=%s b=%s, depth slope %s per unit of b -> b = %r' %
            (r, p, r4fit.tmpl_str(t), r4fit.lin_str(rule['a']), r4fit.lin_str(rule['b']), slope, b2))
        b = b2
    if all_shallow(rules):
        return ('SHALLOWLOOP', 'huge', None, None), huge_events
    raise Unresolved('no halt or cycle after 200 R4 events')


CHAMP_LIST = tuple([1] + [0, 0, 3] * 7 + [0, 0, 2])


def all_shallow(rules):
    """True if no R4 class rebuilds a list whose length grows with b (no deep clearing can follow)"""
    return all(r['kind'] != 'K' or r['list']['alpha'] == 0 for r in rules.values())


def finish(info, S, prev, events, p, rules, outs, notes, say=lambda *a: None, M=None):
    try:
        result, huge_events = abstract_run(S, prev, events, p, rules, outs, say, M, notes)
    except Unresolved as e:
        return dict(info, grade='UNRESOLVED', note=str(e))
    first = events[-1][2] if events else ()
    ell = deepest(first) + 1 if events else 0
    vdeep = first[ell - 1] if events and ell > 0 else 0
    deep_huge = [e for e in huge_events if e[4]]
    R = len(deep_huge)
    slope = deep_huge[0][3] if deep_huge else F(0)
    info.update(events=events, huge=huge_events, R=R, ell=ell, slope=slope)
    nt = ('; ' + '; '.join(notes)) if notes else ''
    if result[0] == 'CYCLE':
        return dict(info, grade='NONHALT-PREDICTED',
                    note='residue dynamics cycles (R4 states repeat); never halts if the rules hold' + nt)
    if result[0] == 'SHALLOWLOOP':
        kf = R + (1 if ell >= 4 else 0)
        info['key'] = (kf, ell, vdeep, slope)
        g = 'BELOW' if (kf, ell, vdeep, slope) < CHAMP_KEY else 'UNRESOLVED'
        return dict(info, grade=g, note='enters a loop of SHALLOW rebuilds (fixed-length lists, exponential steps; '
                    'no R4 class rebuilds a b-dependent list, so at most %d f_omega-scale clearings): halting not '
                    'decided (residue precision), score below f_omega^2(25) either way%s' % (kf, nt))
    if result[0] == 'NORETURN':
        return dict(info, grade='NONHALT-PREDICTED',
                    note='reaches an R4 class with no return to the Kd shape (b %s): runaway, not a record%s' %
                    ('= %d, checked to 1e7 steps' % result[2] if result[1] == 'exact' else 'class %d' % result[2], nt))
    kf = R + (1 if ell >= 4 else 0)
    keyv = (kf, ell, vdeep, slope)
    info['key'] = keyv
    if result[1] == 'exact':
        halt_desc = 'halts at R4 with exact b=%d' % result[2]
    elif result[1] == 'list':
        halt_desc = result[2]
    else:
        halt_desc = 'halts at R4 class %d mod %d, %s' % (result[2], p, r4fit.rule_str(result[3]))
    desc = 'sigma ~ f_omega^%d(%s) [champion f_omega^2(25)] (first list cleared at level f_%s, digit %s; %d deep rebuild(s) '         'from huge counters, slope %s); %s%s' % (kf, ell, ell, vdeep, R, slope, halt_desc, nt)
    if keyv > CHAMP_KEY:
        g = 'BEATS-CHAMPION?'
    elif keyv == CHAMP_KEY:
        same = tuple(first) == CHAMP_LIST and deep_huge and deep_huge[0][2] == '[1,(0,0,3)^(n),0,0,2]'
        g = 'EQUAL' if same else 'EQUAL-KEY'
    else:
        g = 'BELOW'
    return dict(info, grade=g, note=desc)


def fmt_line(r):
    key = r.get('key')
    ks = 'w^%d(%s) v=%s slope=%s' % (key[0], key[1], key[2], key[3]) if key else ''
    ev = r.get('events') or []
    exs = ' '.join('b=%d->[%s]' % (e[1], ','.join(map(str, e[2])) if len(e[2]) <= 40 else
                                   ','.join(map(str, e[2][:40])) + ',...(%d digits)' % len(e[2])) for e in ev)
    hs = ' '.join('class%d:%s(slope %s)' % (h[1], h[2], h[3]) for h in (r.get('huge') or []))
    return '\t'.join([r['machine'], r['grade'], ks, r.get('note', ''), r.get('r4', ''), exs, hs])


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return
    if args[0] == '--list':
        src = args[1]
        out = args[2] if len(args) > 2 and not args[2].startswith('--') else None
        ms = [l.split()[0] for l in open(src) if l.strip()]
        S = hlev.Setup(KBITS)
        fo = open(out, 'w') if out else None
        counts = {}
        for M in ms:
            try:
                r = grade(M, S=S)
            except Exception as e:                      # loud: record the failure, keep going
                r = {'machine': M, 'grade': 'UNRESOLVED', 'note': 'grader error: %r' % e}
            counts[r['grade']] = counts.get(r['grade'], 0) + 1
            line = fmt_line(r)
            if fo:
                fo.write(line + '\n')
                fo.flush()
            if r['grade'].startswith('BEATS') or not fo:
                print(line, flush=True)
        print('SUMMARY', counts, flush=True)
        return
    M = args[0]
    r = grade(M, verbose='-v' in args)
    print(fmt_line(r))


if __name__ == '__main__':
    main()
