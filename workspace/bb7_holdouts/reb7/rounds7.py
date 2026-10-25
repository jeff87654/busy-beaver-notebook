"""rounds7.py: round-by-round residue evaluation of exhaustions (reb7), with class branching.

A world is the accumulator V at a true exhaustion (exact, or Huge known mod some d | Q). The exhaustion class
c = V mod p decides HALT / rebuild / leave; when V's modulus does not determine c, every compatible class is
followed (branching). Verdicts: HALT (every branch halts), NEVER (every branch loops), CLASS-DEPENDENT (some branch
halts, some loops), or UNSETTLED (T / errors / budget)."""
import math
from eng7 import Huge, EngError, modof

LIT_MAX = 3000          # exhaustions with an exact accumulator up to this are run literally


def rebuild_cfg(eng, cls_rule, V, p, c):
    d = cls_rule[1]
    Q = eng.Q
    if isinstance(V, Huge):
        md = V.mod or Q
        if md % p:
            raise EngError('class modulus')
        Qc = md // p
        tr = ((V.r - c) // p) % Qc if (V.r - c) % p == 0 else None
        if tr is None:
            raise EngError('class arithmetic')

        def tv(f):
            al, be = f
            if al == 0:
                return eng.mk(be)
            return Huge((al * tr + be) % Qc, None if Qc == Q else Qc)
    else:
        t = (V - c) // p

        def tv(f):
            return eng.mk(f[0] * t + f[1])
    a, b = tv(d['a']), tv(d['b'])
    if 'fixed' in d:
        return ('fixed', [tv(e) for e in d['fixed']], a, b)
    cnt = tv(d['cnt'])
    if isinstance(cnt, Huge):
        cnt = (cnt.r, cnt.mod or Q)
    return ('struct', d['pre'], d['mid'], cnt, d['suf'], a, b)


def step_world(eng, Efor, V, n, marker, lit):
    """one exhaustion: returns list of (kind, newV, newn, note) branches; kind in H, K, T, ERR"""
    if lit is not None and not isinstance(V, Huge) and V <= LIT_MAX:
        r = lit(V, 0 if marker else n)
        if r[0] == 'H':
            return [('H', None, None, 'literal halt at V=%d' % V)]
        if r[0] != 'K':
            return [('T', None, None, 'literal T at V=%d' % V)]
        ds, a, b = r[1], r[2], r[3]
        try:
            V2 = eng.value(ds, a, b)
            if marker:
                V2 = eng.staircase(V2, len(ds))
        except EngError as e:
            return [('ERR', None, None, str(e))]
        return [('K', V2, len(ds), 'lit V=%d -> n=%d' % (V, len(ds)))]
    E = Efor(n)
    if E is None:
        return [('T', None, None, 'no exhaustion map at n=%s' % (n,))]
    p, cls = E
    if isinstance(V, Huge):
        md = V.mod or eng.Q
        g = math.gcd(md, p)
        classes = [c for c in range(p) if c % g == V.r % g]
    else:
        classes = [V % p]
    out = []
    for c in classes:
        rule = cls[c]
        if rule[0] == 'X':
            if len(classes) == 1:
                out.append(('ERR', None, None, 'exhaustion value in an impossible class %d mod %d' % (c, p)))
            continue
        if rule[0] == 'H':
            out.append(('H', None, None, 'class %d mod %d' % (c, p)))
            continue
        if rule[0] != 'K':
            out.append(('T', None, None, 'class %d leaves template' % c))
            continue
        try:
            if len(classes) > 1:
                # refine V to the class: V mod lcm(md, p) is not known beyond md; the class quotient keeps md/g
                Vc = Huge(c, p) if md == g else None
                if Vc is None:
                    # V = c (mod p) and V = r (mod md): CRT mod lcm, but the known part is md; t mod md/g
                    L = md * p // g
                    for x in range(c, L, p):
                        if x % md == V.r % md:
                            Vc = Huge(x % (md // g * 1), None)
                            break
                    md2 = md // g
                    tr = ((x - c) // p) % md2
                    Vuse = ('class', c, tr, md2)
                else:
                    Vuse = ('class', c, 0, 1)
                cfg = rebuild_cfg_class(eng, rule, Vuse, p)
            else:
                cfg = rebuild_cfg(eng, rule, V, p, c)
            if cfg[0] == 'fixed':
                V2 = eng.value(cfg[1], cfg[2], cfg[3])
                nn = len(cfg[1])
            else:
                V2 = eng.value_struct(cfg[1], cfg[2], cfg[3], cfg[4], cfg[5], cfg[6])
                cnt = cfg[3]
                if isinstance(cnt, tuple):
                    nn = ((len(cfg[1]) + len(cfg[4]) + cnt[0]) % cnt[1], cnt[1])
                else:
                    nn = len(cfg[1]) + len(cfg[4]) + cnt
            if marker:
                V2 = eng.staircase(V2, nn)
            out.append(('K', V2, nn, 'class %d' % c))
        except EngError as e:
            out.append(('ERR', None, None, str(e)))
    return out


def rebuild_cfg_class(eng, rule, Vuse, p):
    """rebuild for a class branch: t = (V - c)/p known mod md2 (md2 = 1: unknown)"""
    _, c, tr, md2 = Vuse
    d = rule[1]
    Q = eng.Q

    def tv(f):
        al, be = f
        if al == 0:
            return eng.mk(be)
        if md2 <= 1:
            return Huge(0, 1)
        return Huge((al * tr + be) % md2, None if md2 == Q else md2)
    a, b = tv(d['a']), tv(d['b'])
    if 'fixed' in d:
        return ('fixed', [tv(e) for e in d['fixed']], a, b)
    cnt = tv(d['cnt'])
    if isinstance(cnt, Huge):
        cnt = (cnt.r, cnt.mod or Q)
    return ('struct', d['pre'], d['mid'], cnt, d['suf'], a, b)


def run_rounds(eng, E, V0, n0=0, marker=False, lit=None, maxr=40, maxnodes=200):
    """E: (p, cls) or a function n -> (p, cls) / None"""
    Efor = E if callable(E) else (lambda n: E)
    """explore worlds; returns (verdict, trace)"""
    trace = []
    frontier = [(V0, n0, 1, ())]
    seen = {}
    nodes = 0
    outcomes = {'H': [], 'LOOP': [], 'T': [], 'ERR': [], 'MAX': []}
    while frontier:
        V, n, rnd, path = frontier.pop()
        nodes += 1
        if nodes > maxnodes:
            outcomes['MAX'].append(path)
            break
        key = (('h', V.r, V.mod) if isinstance(V, Huge) else ('e', V), n if not isinstance(n, tuple) else ('n',) + n)
        if key in seen:
            outcomes['LOOP'].append(path + (('loop', seen[key]),))
            continue
        seen[key] = rnd
        if rnd > maxr:
            outcomes['MAX'].append(path)
            continue
        br = step_world(eng, Efor, V, n, marker, lit)
        trace.append((rnd, repr(V), [b[0] + ':' + b[3] for b in br]))
        for kind, V2, n2, note in br:
            p2 = path + ((rnd, repr(V), note),)
            if kind == 'H':
                outcomes['H'].append(p2)
            elif kind == 'T':
                outcomes['T'].append(p2)
            elif kind == 'ERR':
                outcomes['ERR'].append(p2)
            else:
                frontier.append((V2, n2, rnd + 1, p2))
    nb = {k: len(v) for k, v in outcomes.items() if v}
    if outcomes['H'] and not (outcomes['LOOP'] or outcomes['T'] or outcomes['ERR'] or outcomes['MAX']):
        rmin = min(len(p) for p in outcomes['H'])
        v = 'HALT@%d' % rmin
    elif outcomes['LOOP'] and not (outcomes['H'] or outcomes['T'] or outcomes['ERR'] or outcomes['MAX']):
        v = 'LOOP(%d branches)' % len(outcomes['LOOP'])
    elif outcomes['H'] and outcomes['LOOP']:
        v = 'CLASS-DEPENDENT%s' % nb
    elif outcomes['H']:
        v = 'HALT-SOME%s' % nb
    else:
        v = 'UNSETTLED%s' % nb
    det = {k: [list(map(str, p))[-3:] for p in vv[:2]] for k, vv in outcomes.items() if vv}
    return v, trace + [('outcomes', det)]
