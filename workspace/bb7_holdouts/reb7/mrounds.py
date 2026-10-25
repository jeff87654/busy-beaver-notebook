"""mrounds.py: multi-template exhaustion rounds (reb7 stage for rows whose exhaustion leaves the template).
  python mrounds.py IN.jsonl[,IN2] OUT.jsonl [--only M] [--all]
Templates differ only in the prefix P (same coding u, s, alpha, beta, S). When an exhaustion in template T leaves T,
ffree.exe finds the free prefix P' of the first K-moment after it; T' = T with P = P' gets its own rules (fit7),
engine (eng7) and exhaustion map; the cross map T -> T' is fitted per class with xprobe.exe. States
(template, V mod Q, n) are explored with class branching; a repeated state is a loop.
Verdicts: NEVER-HALTS(residue,multi) / HALT-REACHED(multi) / CLASS-DEPENDENT(multi) / UNSETTLED(multi: ...)."""
import idle  # noqa: F401
import json
import math
import os
import subprocess
import sys
import time

import fit7
import eng7
import rounds7
import reb7
from eng7 import Huge, EngError

HERE = os.path.dirname(os.path.abspath(__file__))
FFREE = os.path.join(HERE, 'ffree.exe')
XPR = os.path.join(HERE, 'xprobe.exe')
Q1, Q2 = reb7.Q1, reb7.Q2


def ta(t):
    return fit7.targs(fit7.parse_template(t))


def unrle(s):
    if s == '-':
        return ''
    out = ''
    for tok in s.split('.'):
        if not tok:
            continue
        if '^' in tok:
            c, k = tok.split('^')
            out += c * int(k)
        else:
            out += tok
    return out


def ffree_first(m, t, ds, a, b, N=200000000):
    inp = '%s %d %d\n' % (','.join(map(str, ds)) if ds else '-', a, b)
    p = subprocess.run([FFREE, m] + ta(t) + [str(N), '2'], input=inp, capture_output=True, text=True,
                       creationflags=0x40, timeout=7200)
    return p.stdout.strip().splitlines()


def xprobe(m, t1, t2, cfgs, N=60000000):
    inp = ''.join('%s %d %d\n' % (','.join(map(str, ds)) if ds else '-', a, b) for ds, a, b in cfgs)
    p = subprocess.run([XPR, m] + ta(t1) + ta(t2) + [str(N)], input=inp, capture_output=True, text=True,
                       creationflags=0x40, timeout=7200)
    out = []
    for l in p.stdout.splitlines():
        f = l.split()
        if f[0] == 'K':
            out.append(('K', [] if f[1] == '-' else [int(x) for x in f[1].split(',')], int(f[2]), int(f[3]), int(f[4])))
        elif f[0] == 'H':
            out.append(('H', int(f[1])))
        else:
            out.append(('T',))
    while len(out) < len(cfgs):
        out.append(('T',))
    return out


class Tpl:
    def __init__(self, world, t):
        self.world = world
        self.t = t
        self.P = fit7.Prober(world.m, t)
        self.R = fit7.fit_rules(self.P)
        self.marker = bool(self.R.get('MB'))
        self.nE = self.R.get('nE', 0)
        self.eng = {}
        self.emaps = {}

    def engine(self, Q):
        if Q not in self.eng:
            self.eng[Q] = eng7.Eng(self.R, Q=Q, JMAX=3000 if Q == Q1 else 1600)
            self.eng[Q].deadline = time.time() + 300
        return self.eng[Q]

    def exh_level(self, n):
        if self.P.Pempty:
            return 0
        if self.marker:
            return self.nE
        return n

    def emap1(self, nn):
        """combined (same template + cross) class map at an exact level nn"""
        if nn in self.emaps:
            return self.emaps[nn]
        _, E = reb7.fit_E2(self.P, self.R, nn, 60)
        if E is None:
            self.emaps[nn] = None
            return None
        p, cls = E
        out = {c: (r + (self.t,) if r[0] == 'K' else r) for c, r in cls.items()}
        tcls = [c for c, r in cls.items() if r[0] == 'T']
        if tcls:
            ds = [0] * nn if not self.P.Pempty else []
            b = 60 + ((tcls[0] - 60) % p)
            lines = ffree_first(self.world.m, self.t, ds, 0, b)
            k = [l for l in lines if l.startswith('K')]
            if k:
                pref = unrle(k[0].split()[2][2:])
                T2 = fit7.parse_template(self.t)
                T2['P'] = pref if pref else '-'
                t2 = fit7.tstr(T2)
                if (not pref or pref[0] == '1') and t2 != self.t:
                    tp2 = self.world.tpl(t2)
                    if tp2 is not None:
                        pat, Ex, _ = fit7.fit_E(self.P, nn, 60, probe=lambda cf: xprobe(self.world.m, self.t, t2, cf),
                                               out_pempty=tp2.P.Pempty)
                        self.world.log.append('cross %s -> %s at n=%s: %s' % (self.t, t2, nn, reb7.e_struct_str(Ex)))
                        if Ex is not None:
                            px, clx = Ex
                            L = p * px // math.gcd(p, px)
                            out2 = {}
                            for c in range(L):
                                r = out[c % p]
                                if r[0] == 'T':
                                    rx = clx[c % px]
                                    r = rx + (t2,) if rx[0] == 'K' else rx
                                    out2[c] = requot(r, c, L, px)
                                else:
                                    out2[c] = requot(r, c, L, p)
                            p, out = L, out2
        self.emaps[nn] = (p, out)
        return self.emaps[nn]

    def emap(self, n):
        if not isinstance(n, tuple):
            return self.emap1(n)
        if 'huge' not in self.emaps:
            maps = {nn: self.emap1(nn) for nn in (24, 25, 26, 27)}
            self.emaps['huge'] = n_affine(maps)
            self.world.log.append('n-affine map at huge n (%s): %s' % (self.t[:24], 'ok' if self.emaps['huge'] else 'FAILED'))
        return self.emaps['huge']


def gstruct(rule):
    """class rule ('K', d, ...) -> unified struct {'pre': [(al,be)], 'mid': v|None, 'cnt': (al,be), 'suf': [...], 'a', 'b'}"""
    d = rule[1]
    if 'fixed' in d:
        E = [tuple(e) for e in d['fixed']]
        best = None
        i = 0
        while i < len(E):
            j = i
            while j < len(E) and E[j] == E[i] and E[i][0] == 0:
                j += 1
            if j - i >= 3 and (best is None or j - i > best[1] - best[0]):
                best = (i, j)
            i = max(j, i + 1)
        if best is None:
            g = {'pre': E, 'mid': None, 'cnt': (0, 0), 'suf': []}
        else:
            g = {'pre': E[:best[0]], 'mid': E[best[0]][1], 'cnt': (0, best[1] - best[0]), 'suf': E[best[1]:]}
    else:
        g = {'pre': [(0, x) for x in d['pre']], 'mid': d['mid'], 'cnt': tuple(d['cnt']), 'suf': [(0, x) for x in d['suf']]}
    g['a'], g['b'] = tuple(d['a']), tuple(d['b'])
    return g


def n_affine(maps):
    """maps {n: (p, cls)} at several n -> (p, cls) with cls[c] = ('K3', g3, tid) where every coefficient triple is
    (al, be0, be1): value = al t + be0 + be1 n; or None if not affine in n"""
    ns = sorted(maps)
    if any(maps[n] is None for n in ns):
        return None
    ps = set(maps[n][0] for n in ns)
    if len(ps) != 1:
        return None
    p = ps.pop()
    out = {}
    for c in range(p):
        rs = [maps[n][1][c] for n in ns]
        kinds = set(r[0] for r in rs)
        if len(kinds) != 1:
            return None
        if rs[0][0] != 'K':
            out[c] = rs[0]
            continue
        tids = set(r[2] for r in rs)
        if len(tids) != 1:
            return None
        gs = [gstruct(r) for r in rs]
        if len(set((len(g['pre']), len(g['suf']), g['mid']) for g in gs)) != 1:
            return None

        def fitn(pairs):
            als = set(x[0] for x in pairs)
            if len(als) != 1:
                return None
            f = fit7.fit_line([(n, x[1]) for n, x in zip(ns, pairs)])
            return None if f is None else (pairs[0][0], f[1], f[0])
        g3 = {}
        for key in ('cnt', 'a', 'b'):
            v = fitn([g[key] for g in gs])
            if v is None:
                return None
            g3[key] = v
        for key in ('pre', 'suf'):
            lst = []
            for i in range(len(gs[0][key])):
                v = fitn([g[key][i] for g in gs])
                if v is None:
                    return None
                lst.append(v)
            g3[key] = lst
        g3['mid'] = gs[0]['mid']
        out[c] = ('K3', g3, rs[0][2])
    return (p, out)


def rebuild3(eng, g3, V, p, c, n):
    """evaluate an n-affine rule: t = (V - c)/p (exact or mod), n exact or (r, mod)"""
    Q = eng.Q
    if isinstance(V, Huge):
        md = V.mod or Q
        tq = (((V.r - c) // p) % (md // p), md // p)
    else:
        tq = ((V - c) // p, None)
    nq = n if isinstance(n, tuple) else (n, None)

    def ev(f):
        al, b0, b1 = f
        mods = [m for m in ((tq[1] if al else None), (nq[1] if b1 else None)) if m]
        if not mods:
            return eng.mk(al * tq[0] + b0 + b1 * nq[0])
        md = mods[0]
        for m in mods[1:]:
            md = math.gcd(md, m)
        return Huge((al * tq[0] + b0 + b1 * nq[0]) % md, None if md == Q else md)
    pre = [ev(f) for f in g3['pre']]
    suf = [ev(f) for f in g3['suf']]
    a, b = ev(g3['a']), ev(g3['b'])
    cnt = ev(g3['cnt']) if g3['mid'] is not None else 0
    return pre, g3['mid'], cnt, suf, a, b


def requot(rule, c, L, p0):
    """a class rule fitted with modulus p0 (t0 = (V - c0)/p0, c0 = c mod p0) re-expressed with modulus L:
    t0 = (L t + c - c0)/p0 = (L/p0) t + (c - c0)/p0"""
    if rule[0] != 'K' or L == p0:
        return rule
    c0 = c % p0
    k1, k0 = L // p0, (c - c0) // p0
    d = dict(rule[1])

    def sh(f):
        al, be = f
        return (al * k1, be + al * k0)
    nd = {}
    for kk, v in d.items():
        if kk in ('pre', 'suf', 'mid'):
            nd[kk] = v
        elif kk == 'fixed':
            nd[kk] = [sh(e) for e in v]
        else:
            nd[kk] = sh(v)
    return (rule[0], nd) + rule[2:]


class World:
    def __init__(self, m):
        self.m = m
        self.tpls = {}
        self.log = []

    def tpl(self, t):
        if t not in self.tpls:
            if len(self.tpls) >= 4:
                return None
            for attempt in (1, 2):
                try:
                    self.tpls[t] = Tpl(self, t)
                    break
                except fit7.FitError as e:
                    self.log.append('nofit %s (attempt %d): %s' % (t, attempt, e))
                    self.tpls[t] = None
        return self.tpls[t]


def step(world, Q, tid, V, n):
    tp = world.tpls[tid]
    nE = tp.exh_level(n)
    E = tp.emap(nE)
    if E is None:
        return [('T', None, None, None, 'no exhaustion map %s n=%s' % (tid, n))]
    p, cls = E
    if isinstance(V, Huge):
        md = V.mod or Q
        g = math.gcd(md, p)
        classes = [c for c in range(p) if c % g == V.r % g]
    else:
        classes = [V % p]
    out = []
    for c in classes:
        rule = cls[c]
        if rule[0] == 'K3':
            if len(classes) > 1:
                out.append(('ERR', None, None, None, 'class branching with an n-affine rule'))
                continue
            t2 = rule[2]
            tp2 = world.tpls[t2]
            e2 = tp2.engine(Q)
            try:
                pre, mid, cnt, suf, a, b = rebuild3(e2, rule[1], V, p, c, n)
                if mid is None:
                    V2 = e2.value(pre + suf, a, b)
                    nn = len(pre) + len(suf)
                else:
                    cq = (cnt.r, cnt.mod or Q) if isinstance(cnt, Huge) else cnt
                    V2 = e2.value_struct(pre, mid, cq, suf, a, b)
                    if isinstance(cq, tuple):
                        nn = ((len(pre) + len(suf) + cq[0]) % cq[1], cq[1])
                    else:
                        nn = len(pre) + len(suf) + cq
                if tp2.marker:
                    V2 = e2.staircase(V2, nn)
                out.append(('K', t2, V2, nn, 'class %d -> %s (n-affine)' % (c, t2[:14])))
            except EngError as e:
                out.append(('ERR', None, None, None, str(e)))
            continue
        if rule[0] in ('H', 'T', 'X'):
            out.append((rule[0], None, None, None, 'class %d mod %d (%s)' % (c, p, tid[:12])))
            continue
        t2 = rule[2]
        tp2 = world.tpls[t2]
        e2 = tp2.engine(Q)
        try:
            if len(classes) > 1:
                md = V.mod or Q
                g = math.gcd(md, p)
                L = md * p // g
                x = next(x for x in range(c, L, p) if x % md == V.r % md)
                cfg = rounds7.rebuild_cfg_class(e2, rule[:2], ('class', c, ((x - c) // p) % (md // g), md // g), p)
            else:
                cfg = rounds7.rebuild_cfg(e2, rule[:2], V, p, c)
            if cfg[0] == 'fixed':
                V2 = e2.value(cfg[1], cfg[2], cfg[3])
                nn = len(cfg[1])
            else:
                V2 = e2.value_struct(cfg[1], cfg[2], cfg[3], cfg[4], cfg[5], cfg[6])
                cnt = cfg[3]
                nn = ((len(cfg[1]) + len(cfg[4]) + cnt[0]) % cnt[1], cnt[1]) if isinstance(cnt, tuple) else \
                    len(cfg[1]) + len(cfg[4]) + cnt
            if tp2.marker:
                V2 = e2.staircase(V2, nn)
            out.append(('K', t2, V2, nn, 'class %d -> %s' % (c, t2[:14])))
        except EngError as e:
            out.append(('ERR', None, None, None, str(e)))
    return out


def run(world, Q, t0, V0, n0, maxnodes=200, maxr=40):
    frontier = [(t0, V0, n0, 1, ())]
    seen = {}
    res = {'H': [], 'LOOP': [], 'T': [], 'ERR': [], 'MAX': []}
    nodes = 0
    trace = []
    seenV = {}
    while frontier:
        tid, V, n, rnd, path = frontier.pop()
        nodes += 1
        if nodes > maxnodes or rnd > maxr:
            res['MAX'].append(path)
            continue
        vkey = ('h', V.r, V.mod) if isinstance(V, Huge) else ('e', V)
        key = (tid, vkey, n if not isinstance(n, tuple) else n)
        if key in seen:
            res['LOOP'].append(path)
            continue
        seen[key] = rnd
        if (tid, vkey) in seenV and isinstance(n, tuple):
            # same template and accumulator, different (huge) list length: if the step from (tid, V) does not depend
            # on n (all sampled residues of n give the same outcome kinds and next accumulators), the outcome sequence
            # from here repeats the one already explored -> loop
            import random
            rnd_ = random.Random(1)
            outs = set()
            for _ in range(24):
                nr = (rnd_.randrange(n[1]), n[1])
                br = step(world, Q, tid, V, nr)
                outs.add(tuple((b[0], b[1], repr(b[2])) for b in br))
            if len(outs) == 1:
                res['LOOP'].append(path + (('n-independent repeat',),))
                continue
        seenV[(tid, vkey)] = rnd
        br = step(world, Q, tid, V, n)
        trace.append((rnd, tid[:16], repr(V), [b[0] + ':' + b[4] for b in br]))
        for kind, t2, V2, n2, note in br:
            p2 = path + ((rnd, note),)
            if kind == 'K':
                frontier.append((t2, V2, n2, rnd + 1, p2))
            else:
                res[{'H': 'H', 'T': 'T', 'X': 'ERR', 'ERR': 'ERR'}[kind]].append(p2)
    nb = {k: len(v) for k, v in res.items() if v}
    if res['H'] and not (res['LOOP'] or res['T'] or res['ERR'] or res['MAX']):
        v = 'HALT@%d' % min(len(p) for p in res['H'])
    elif res['LOOP'] and not (res['H'] or res['T'] or res['ERR'] or res['MAX']):
        v = 'LOOP(%d)' % len(res['LOOP'])
    elif res['H'] and res['LOOP']:
        v = 'CLASS-DEPENDENT%s' % nb
    elif res['H']:
        v = 'HALT-SOME%s' % nb
    else:
        v = 'UNSETTLED%s' % nb
    return v, trace


def analyse(r):
    t0 = time.time()
    m, t = r['machine'], r['tmpl']
    world = World(m)
    tp = world.tpl(t)
    row = {'machine': m, 'tmpl': t}
    if tp is None:
        row['verdict'] = 'NOFIT'
        return row
    ks, end = tp.P.trace(300000000, 3000)
    start = (ks[-1][1], ks[-1][2], ks[-1][3])
    out = {}
    for Q in (Q1, Q2):
        e = tp.engine(Q)
        try:
            V = e.value(*start)
            if tp.marker:
                V = e.staircase(V, len(start[0]))
            out[Q] = run(world, Q, t, V, len(start[0]))
        except EngError as ex:
            out[Q] = ('ERR: %s' % ex, [])
    row['templates'] = {k: (None if v is None else {'rules': reb7.rules_str(v.R), 'marker': v.marker, 'nE': v.nE,
                                                     'mscan': v.R.get('mscan')}) for k, v in world.tpls.items()}
    row['log'] = world.log
    row['rounds'] = {str(Q): (out[Q][0], [list(map(str, x)) for x in out[Q][1][:10]]) for Q in out}
    v1, v2 = out[Q1][0], out[Q2][0]
    fl = []
    for v in world.tpls.values():
        if v:
            for e in v.eng.values():
                fl += e.flags[:2]
    row['flags'] = fl[:6]
    if v1.startswith('HALT@') or v2.startswith('HALT@'):
        verdict = 'HALT-REACHED(multi %s/%s)' % (v1, v2)
    elif any(x.startswith(('CLASS-DEPENDENT', 'HALT-SOME')) for x in (v1, v2)):
        verdict = 'CLASS-DEPENDENT(multi %s | %s)' % (v1, v2)
    elif v1.startswith('LOOP') and not fl:
        verdict = 'NEVER-HALTS(residue,multi)' + ('+Q2' if v2.startswith('LOOP') else '')
    else:
        verdict = 'UNSETTLED(multi %s | %s)' % (v1[:80], v2[:40])
    row['verdict'] = verdict
    row['ntemplates'] = len([x for x in world.tpls.values() if x])
    row['time'] = round(time.time() - t0, 1)
    return row


def main():
    ins = sys.argv[1].split(',')
    out = sys.argv[2]
    only = sys.argv[sys.argv.index('--only') + 1] if '--only' in sys.argv else None
    done = set()
    if os.path.exists(out):
        done = set(json.loads(l)['machine'] for l in open(out))
    rows = []
    for fn in ins:
        for l in open(fn):
            r = json.loads(l)
            if r['machine'] in done or (only and r['machine'] != only):
                continue
            rq = str(r.get('rounds', {}).get('80640', ['-'])[0]) if r.get('rounds') else ''
            if "'T'" in rq or rq.startswith('T@') or '--all' in sys.argv:
                if 'tmpl' in r:
                    rows.append(r)
    sys.setrecursionlimit(100000)
    with open(out, 'a', newline='\n') as fo:
        for r in rows:
            try:
                row = analyse(r)
            except Exception:  # noqa
                import traceback
                row = {'machine': r['machine'], 'verdict': 'ERROR', 'err': traceback.format_exc()[-800:]}
            fo.write(json.dumps(row, default=str) + '\n')
            fo.flush()
            print(r['machine'], row.get('verdict'), row.get('ntemplates'), row.get('time'), flush=True)


if __name__ == '__main__':
    main()
