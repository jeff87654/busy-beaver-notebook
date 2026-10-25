"""h14verify abstract simulator: B-form configurations with affine huge values; Coq macros CLR / PERIOD;
all other stages literal (stage.exe) under several representative assignments + affine fit (uniformity check)."""
import subprocess, random, sys, time, os
from fractions import Fraction as Fr
from ures import *
HERE = os.path.dirname(os.path.abspath(__file__))
H14 = os.environ.get('TM', '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_0LK0LC_0LN1LL_0LK1LM_1RJ1RM_1RD---')
MREP = int(os.environ.get('MREP', 840))
GROW = int(os.environ.get('GROW', 3))
MAXS = int(float(os.environ.get('MAXS', 2e10)))
REPMODE = os.environ.get('REPMODE', 'geo')


class Runner:
    def __init__(self):
        self.p = subprocess.Popen([os.path.join(HERE, 'stage_t12v.exe')], stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, text=True, bufsize=1)

    def run(self, tm, q, head, tape, maxs):
        self.p.stdin.write('%s %s %d %d %s\n' % (tm, q, head, maxs, tape or '-'))
        self.p.stdin.flush()
        f = self.p.stdout.readline().split()
        if len(f) < 6:
            open(os.path.join(HERE, 'crash_input.txt'), 'w').write(' '.join([tm, q, str(head), str(maxs), tape or '-']))
            raise RuntimeError('stage.exe died; input saved to crash_input.txt')
        return dict(kind=f[0], steps=int(f[1]), q=f[2], rel=int(f[3]), sym=int(f[4]), lo=int(f[5]),
                    word='' if f[6] == '-' else f[6])


RUN = None


def tokens(word):
    out = []
    i = 0
    n = len(word)
    while i < n:
        if word[i] == '0':
            j = i
            while j < n and word[j] == '0':
                j += 1
            out.append(('z', j - i))
            i = j
            continue
        j = i
        m = 0
        while j + 2 < n and word[j + 1] == '0' and word[j + 2] == '1':
            j += 2
            m += 1
        out.append(('t', m))
        i = j + 1
    return out


def group(toks):
    runs = []
    for kind, v in toks:
        if kind == 't' and runs and runs[-1][0] == 't' and runs[-1][1] == v:
            runs[-1][2] += 1
        elif kind == 't':
            runs.append(['t', v, 1])
        else:
            runs.append(['z', v])
    runs = [tuple(r) for r in runs]
    # compress repeated blocks of 2..4 runs (>= 3 repetitions) into ('R', block, count)
    out = []
    i = 0
    while i < len(runs):
        done = False
        for p in range(2, 17):
            blk = runs[i:i + p]
            if len(blk) < p:
                break
            c = 1
            while runs[i + c * p: i + (c + 1) * p] == blk:
                c += 1
            if c >= 3:
                out.append(('R', tuple(blk), c))
                i += c * p
                done = True
                break
        if not done:
            out.append(runs[i])
            i += 1
    return out


def render(runs, reps):
    out = []
    for r in runs:
        if r[0] == 'R':
            c = Val.of(r[2]).at(reps)
            out.append(render(list(r[1]), reps) * c)
        elif r[0] == 't':
            v, c = Val.of(r[1]).at(reps), Val.of(r[2]).at(reps)
            assert v >= 0 and c >= 0, (r, v, c)
            out.append(('10' * v + '1') * c)
        else:
            n = Val.of(r[1]).at(reps)
            assert n >= 1
            out.append('0' * n)
    return ''.join(out)


def atoms_of(runs):
    s = set()
    for r in runs:
        for x in r[1:]:
            if isinstance(x, Val):
                s.update(x.co)
            if isinstance(x, tuple):
                for y in x:
                    for z in y[1:]:
                        if isinstance(z, Val):
                            s.update(z.co)
    return sorted(s, key=lambda k: ATOMS[k]['rank'])


def show(runs, lim=40):
    out = []
    for r in runs:
        if r[0] == 'R':
            out.append('(%s)^%s' % (show(list(r[1])), Val.of(r[2])))
        elif r[0] == 't':
            c = Val.of(r[2])
            s = str(Val.of(r[1]))
            out.append(s if c == 1 else '%s^%s' % (s, c))
        else:
            out.append('z%s' % Val.of(r[1]))
    if len(out) > lim:
        out = out[:lim // 2] + ['...'] + out[-lim // 2:]
    return ' '.join(out)


def norm(runs):
    """merge adjacent equal token runs; drop zero counts"""
    out = []
    for r in runs:
        if r[0] == 'R':
            out.append(('R', r[1], Val.of(r[2])))
            continue
        r = tuple(Val.of(x) if not isinstance(x, str) else x for x in r)
        if r[0] == 't' and r[2] == 0:
            continue
        if r[0] == 't' and out and out[-1][0] == 't' and out[-1][1] == r[1]:
            out[-1] = ('t', r[1], out[-1][2] + r[2])
        else:
            out.append(r)
    return out


def rep_sets(atoms, ntr, seed=0):
    """trial rep maps: base (slots GROW^i by magnitude rank), one bump per atom, plus random trials"""
    if REPMODE == 'lin':
        base = {a: 1 + 2 * i for i, a in enumerate(atoms)}
    else:
        base = {a: GROW ** i for i, a in enumerate(atoms)}
    sets = [dict(base)]
    for a in atoms:
        s = dict(base)
        s[a] += 1
        sets.append(s)
    rnd = random.Random(len(atoms) * 7919 + ntr + seed)
    for _ in range(ntr):
        sets.append({a: base[a] + rnd.randint(0, 1 if REPMODE == 'lin' else max(1, GROW ** atoms.index(a) // 2)) for a in atoms})
    for a in atoms:
        assert ATOMS[a]['mod'] % MREP == 0
    return [{a: ATOMS[a]['res'] % MREP + MREP * s[a] for a in atoms} for s in sets]


class NonUniform(Exception):
    pass


def literal_stage(runs, tm=H14, q='H', head=None, ntr=2, maxs=None, seed=0):
    """run one literal stage from a configuration (default: B-form, head at the right end) under several reps;
    returns (kind, out_runs as Vals, info)"""
    global RUN
    if RUN is None:
        RUN = Runner()
    atoms = atoms_of(runs)
    reps = rep_sets(atoms, ntr, seed)
    res = []
    for rp in reps:
        tape = render(runs, rp)
        h = len(tape) if head is None else head(rp)
        t0 = time.time()
        r = RUN.run(tm, q, h, tape, maxs or MAXS)
        r['time'] = time.time() - t0
        r['len'] = len(tape)
        res.append(r)
        if r['kind'] == 'T':
            break
    kinds = set((r['kind'], r['q'], r['sym']) for r in res)
    info = dict(steps=[r['steps'] for r in res], time=sum(r['time'] for r in res),
                lens=[r['len'] for r in res], lo=[r['lo'] for r in res], reps=reps, atoms=atoms)
    if res[-1]['kind'] in 'TX':
        return 'T', None, info
    if len(kinds) > 1:
        raise NonUniform('kinds differ %s' % kinds)
    kind = res[0]['kind']
    outs = [group(tokens(r['word'])) for r in res]
    rels = [r['rel'] - len(r['word']) for r in res]
    if kind == 'B':
        assert all(x == 0 for x in rels)
    shapes = set(tuple((x[0], len(x)) for x in o) for o in outs)
    if len(shapes) > 1:
        raise NonUniform('shapes differ: ' + ' || '.join(
            ' '.join('%s%s' % (x[0], x[1:]) for x in o)[:400] for o in outs))

    def fit(nums):
        o0 = nums[0]
        co = {}
        for i, a in enumerate(atoms):
            co[a] = Fr(nums[1 + i] - o0, MREP)
        c = o0 - sum(co[a] * reps[0][a] for a in atoms)
        v = Val(c, co)
        for j in range(len(reps)):
            try:
                ok = v.at(reps[j]) == nums[j]
            except AssertionError:
                ok = False
            if not ok:
                raise NonUniform('affine fit fails: %s' % (nums,))
        return v
    fitted = []
    for idx in range(len(outs[0])):
        items = [o[idx] for o in outs]
        if items[0][0] == 'R':
            if len(set(x[1] for x in items)) != 1:
                raise NonUniform('block contents differ %s' % (items,))
            fitted.append(('R', items[0][1], fit([x[2] for x in items])))
        elif items[0][0] == 't':
            fitted.append(('t', fit([x[1] for x in items]), fit([x[2] for x in items])))
        else:
            fitted.append(('z', fit([x[1] for x in items])))
    info['rel'] = fit(rels) if kind != 'B' else 0
    info['q'] = res[0]['q']
    info['sym'] = res[0]['sym']
    info['lofit'] = fit([r['lo'] for r in res])
    return kind, norm(fitted), info


# ---------------------------------------------------------------- B-form helpers
def pop_tok(runs):
    """split off the last token: returns (value, rest) or None if the last run is a gap"""
    if not runs or runs[-1][0] != 't':
        return None
    k, v, c = runs[-1]
    rest = list(runs[:-1])
    c1 = Val.of(c) - 1
    if not (c1 == 0):
        rest = rest + [('t', v, c1)]
    return v, rest


def is_bform(runs):
    p = pop_tok(runs)
    if not p:
        return False
    q = pop_tok(p[1])
    return q is not None and q[0] == 0


def ge3(v):
    v = Val.of(v)
    return v.huge() or v.ival() >= 3


def clr(runs):
    """Coq CLR: [L, c+3d, 1^n | A] -> [L, c, 1^n | iter d (U n) A]  (d >= 1, n = 0 or A = 1 mod 3)"""
    A, r = pop_tok(runs)
    z, r = pop_tok(r)
    n = Val(0)
    if r and r[-1][0] == 't' and r[-1][1] == 1:
        n = Val.of(r[-1][2])
        r = r[:-1]
    p = pop_tok(r)
    if p is None:
        return None
    T, r = p
    T = Val.of(T)
    if not ge3(T):
        return None
    c = T.res(3)
    if not (n == 0) and Val.of(A).res(3) != 1:
        return ('noclr-A', None, None)
    d = (T - c).div(3)
    newA = iterU(d, n, A, note='CLR d=%r n=%r' % (d, n))
    out = r + [('t', Val(c), Val(1))]
    if not (n == 0):
        out.append(('t', Val(1), n))
    out += [('t', Val(0), Val(1)), ('t', newA, Val(1))]
    return ('clr', norm(out), dict(d=d, n=n, A=A, newA=newA, c=c))


def stable_phi(m):
    return (3 * tau(m) - 8) % m


PREFIX_OK = set()


def prefix_key(prefix):
    return tuple((r[0],) + tuple((Val.of(x).key() if not isinstance(x, tuple) else repr(x)) for x in r[1:]) for r in prefix)


def per_match(runs):
    """split runs into (prefix, k, m, n, a) if they end in the Per pattern 2^k 5 1^m 0 0 2 1^n 0 a"""
    pat = [('t', 2), ('t', 5), ('t', 1), ('t', 0), ('t', 2), ('t', 1), ('t', 0), ('t', None)]
    if len(runs) < 8:
        return None
    tail = runs[-8:]
    for (kd, v), r in zip(pat, tail):
        if r[0] != kd or (v is not None and not (r[1] == v)):
            return None
    cnts = [Val.of(r[2]) for r in tail]
    if not (cnts[1] == 1 and cnts[3] == 2 and cnts[4] == 1 and cnts[6] == 1 and cnts[7] == 1):
        return None
    return list(runs[:-8]), cnts[0], cnts[2], cnts[5], Val.of(tail[7][1])


def period_macro(runs):
    """Coq PERIODS: Per k (14J+r) n a -->* Per (k+4J) r n' a', r in 7..20, if the tape is exactly Per k m n a.
    With a non-empty prefix only when PREFIX_OK holds that prefix (one literal period checked, see drive.py)."""
    pm = per_match(runs)
    if pm is None:
        return None
    prefix = pm[0]
    if prefix and prefix_key(prefix) not in PREFIX_OK:
        return ('noinv', 'prefix not validated', None)
    pat = [('t', 2), ('t', 5), ('t', 1), ('t', 0), ('t', 2), ('t', 1), ('t', 0), ('t', None)]
    runs = runs[len(prefix):]
    if len(runs) != 8:
        return None
    for (kd, v), r in zip(pat, runs):
        if r[0] != kd or (v is not None and not (r[1] == v)):
            return None
    cnts = [Val.of(r[2]) for r in runs]
    if not (cnts[1] == 1 and cnts[3] == 2 and cnts[4] == 1 and cnts[6] == 1 and cnts[7] == 1):
        return None
    k, m, n, a = cnts[0], cnts[2], cnts[5], Val.of(runs[7][1])
    if not m.huge() and m.ival() < 21:
        return None
    if not n.huge() and n.ival() < 3:
        return ('noinv', 'n small', None)
    if a.res(3) != 1:
        return ('noinv', 'a mod 3', None)
    if not (len(a.co) == 1 and a.c == 0 and list(a.co.values())[0] == 1 and ATOMS[list(a.co)[0]]['geU'] == n):
        return ('noinv', 'a >= U n 4 not established', None)
    r = 7 + (m - 7).res(14)
    J = (m - r).div(14)
    out = None
    divs = sorted(set(2 ** a * 3 ** b * 7 ** c for a in range(5) for b in range(1, 7) for c in range(3)))
    for dv in divs:
        mm = MB // dv
        try:
            phi3 = stable_phi(3 * mm)
            ups = ((phi3 - 1) // 3) % mm
            p0 = (a - 1).div(3).res(mm)
            Jr = J.res(mm)
            nres = (n.res(mm) + 2 * p0 + 2 * ups + 2 + (Jr - 1) * (4 * ups + 2)) % mm
            out = (nres, mm, stable_phi(mm))
            break
        except ValueError:
            continue
    if out is None:
        raise ValueError('precision in PERIOD')
    nres, mm, ares = out
    top = max([x['rank'] for x in ATOMS.values() if x.get('tier', 'real') == 'real'] + [1000])
    n2 = new_atom('n', nres, mm, rank=top + 1, note='depth after PERIODS')
    a2 = new_atom('a', ares, mm, rank=top + 2, note='acc after PERIODS', geU=n2)
    new = [('t', Val(2), k + 4 * J), ('t', Val(5), Val(1)), ('t', Val(1), Val(r)), ('t', Val(0), Val(2)),
           ('t', Val(2), Val(1)), ('t', Val(1), n2), ('t', Val(0), Val(1)), ('t', a2, Val(1))]
    return ('period', norm(list(prefix) + new), dict(J=J, r=r, k=k, n=n, a=a, prefix=len(prefix)))


# ---------------------------------------------------------------- re-atomization (keeps representatives small)
from math import gcd as _gcd


def _den(v):
    d = v.c.denominator
    for c in v.co.values():
        d = d * c.denominator // _gcd(d, c.denominator)
    return d


def reatomize(runs, allowed=3, log=None):
    """replace every Val whose coefficient denominators do not divide `allowed` by fresh atom + integer const; Vals with
    the same coefficient vector share one atom (token X and count X+1 stay related). Exact residues are kept."""
    fam = {}

    def conv(v):
        v = Val.of(v)
        realc = [c for a, c in v.co.items() if ATOMS[a].get('tier', 'real') == 'real']
        mixed = any(c > 0 for c in realc) and any(c < 0 for c in realc)
        if not v.co or (allowed % _den(Val(0, v.co)) == 0 and not mixed):
            return v
        key = tuple(sorted(v.co.items()))
        if key not in fam:
            cint = v.c.numerator // v.c.denominator
            core = v - cint
            r, m = best_res(core)
            dom = max([a for a in v.co if v.co[a] > 0] or list(v.co), key=lambda a: ATOMS[a]['rank'])
            rk = ATOMS[dom]['rank'] + (0.25 if abs(v.co[dom]) > 1 else -0.25)
            at = new_atom('X', r, m, rank=rk, note='reatom %r' % core)
            ATOMS[list(at.co)[0]]['tier'] = ATOMS[dom].get('tier', 'real')
            fam[key] = (at, core.c)
            if log:
                log('      reatom %s := %r (residue mod %d)' % (ATOMS[list(at.co)[0]]['name'], core, m))
        at, c0 = fam[key]
        d = v.c - c0
        assert d.denominator == 1
        return at + d

    out = []
    for r in runs:
        if r[0] == 'R':
            out.append(('R', r[1], conv(r[2])))
        elif r[0] == 't':
            out.append(('t', conv(r[1]), conv(r[2])))
        else:
            out.append(('z', conv(r[1])))
    return norm(out), bool(fam)
