"""reb7.py: rebuild-then-halt triage of digit-list rebuilders (BB(7) holdouts).

  python reb7.py POOL.tsv OUT.jsonl [--only M] [--limit N] [--shard i/n]
POOL rows: machine \t template \t tag... ; results appended to OUT.jsonl (resumable: machines already in OUT are
skipped). Per machine:
  1. rule fit (fit7) on the template and its P-absorbing variants (first variant that fits all rules wins)
  2. literal trace from the blank tape (3e8 steps / 3000 K-configs): lockstep vs rules; literal exhaustions
  3. random literal configurations (borrows over up to 12 zeros)
  4. exhaustion map E per class (b = 60..107, re-checked at b = 300..347); n-dependence for P nonempty
  5. residue rounds (eng7/rounds7) from the last literal K-configuration with Q1 = 80640 and Q2 = 443520
  6. linear invariant search mod 2,3,4,6 over (a, b, sum ds, len ds), including the rebuild map
"""
import idle  # noqa: F401
import argparse
import json
import math
import os
import random
import sys
import time
import traceback

import fit7
import eng7
import rounds7

Q1, Q2 = 80640, 483840


def lockstep(P, R, ks):
    bad, exh = [], []
    for i in range(len(ks) - 1):
        nx = fit7.rule_next(R, (ks[i][1], ks[i][2], ks[i][3]))
        if nx[0] == 'K' and nx[2] == 0 and not any(nx[1]):
            nx = ('E', len(nx[1]), nx[3])          # D/R2 step straight into the exhaustion: composite with E
        if nx[0] == 'E':
            exh.append((ks[i][0], nx[2], len(ks[i + 1][1]), ks[i + 1][1][:6], ks[i + 1][2], ks[i + 1][3]))
            continue
        if not (fit7.norm(nx[1], P.Pempty) == fit7.norm(ks[i + 1][1], P.Pempty) and nx[2] == ks[i + 1][2]
                and nx[3] == ks[i + 1][3]):
            bad.append((i, ks[i][0], ks[i][1][:12], ks[i][2], ks[i][3], nx[4]))
    return bad, exh


def e_struct_str(E):
    if E is None:
        return '-'
    p, cls = E
    out = []
    for c in range(p):
        r = cls[c]
        if r[0] != 'K':
            out.append('%d:%s' % (c, r[0]))
        else:
            d = r[1]
            if 'fixed' in d:
                out.append('%d:[%s];a=%s;b=%s' % (c, ','.join('%dt%+d' % e for e in d['fixed']), '%dt%+d' % tuple(d['a']),
                                                  '%dt%+d' % tuple(d['b'])))
            else:
                out.append('%d:[%s%d^(%dt%+d)%s];a=%s;b=%s' % (
                    c, ''.join('%d,' % x for x in d['pre']), d['mid'], d['cnt'][0], d['cnt'][1],
                    ''.join(',%d' % x for x in d['suf']), '%dt%+d' % tuple(d['a']), '%dt%+d' % tuple(d['b'])))
    return 'mod %d (b=%d t+c): ' % (p, p) + ' | '.join(out)


def rules_str(R):
    s = 'D b->%db%+d | R2 a=%db%+d b=%db%+d' % (R['F0'] + R['A2'] + R['B2'])
    p = R['Bpat']
    s += ' | Bk x=%db%+d%+dk tail=%s%s^*%s a=%s b=%s' % (p['m'], p['x0'], p['x1'], p['head'], p['mid'], p['end'],
                                                       '%db%+d' % tuple(p['a']), '%db%+d' % tuple(p['b']))
    for k in sorted(R['B']):
        L, fa, fb = eng7.borrow_rule(R, k)
        p2 = R['Bpat']
        if k >= p2['k0']:
            continue
        s += ' | B%d=%s a=%s b=%s' % (k, [tuple(e) for e in R['B'][k]['L']], tuple(fa), tuple(fb))
    return s


def signature(R, E):
    """family key: rules + exhaustion map"""
    p = R['Bpat']
    bks = tuple((k, tuple(tuple(e) for e in R['B'][k]['L']), tuple(R['B'][k]['a']), tuple(R['B'][k]['b']))
                for k in sorted(R['B']) if k < p['k0'])
    return json.dumps([R['F0'], R['A2'], R['B2'], R.get('excR2'), bks,
                       [p['m'], p['x0'], p['x1'], p['head'], p['mid'], p['end'], p['a'], p['b']],
                       e_struct_str(E)], default=list)


def find_invariants(R, E, mods=(2, 3, 4, 6), trials=500, seed=7):
    """Phi = ca a + cb b + cd sum(ds) + cn len(ds) mod m preserved by D, R2, Bk (k up to 15) and by every rebuild."""
    rnd = random.Random(seed)
    steps = []
    for _ in range(trials):
        r = rnd.random()
        if r < 0.5:
            k = rnd.randint(1, 15)
            ds = [rnd.randint(1, 5)] + [rnd.randint(0, 5) for _ in range(rnd.randint(0, 3))] + [rnd.randint(1, 5)] + [0] * k
            a, b = 0, rnd.randint(3 * k + 6, 3 * k + 80)
        else:
            n = rnd.randint(1, 6)
            ds = [rnd.randint(1, 5)] + [rnd.randint(0, 5) for _ in range(n - 1)]
            a, b = rnd.randint(0, 6), rnd.randint(10, 80)
        if R.get('MB') and rnd.random() < 0.15:
            ds, a, b = [0] * rnd.randint(1, 15), 0, rnd.randint(60, 140)
        nx = fit7.rule_next(R, (ds, a, b))
        if nx[0] == 'K' and min(nx[1] + [nx[2], nx[3]]) >= 0:
            steps.append(((ds, a, b), (nx[1], nx[2], nx[3])))
    ex = []
    if E:
        p, cls = E
        for V in range(200, 200 + 6 * p):
            c = V % p
            rr = cls[c]
            if rr[0] == 'K':
                t = (V - c) // p
                d = rr[1]
                if 'fixed' in d:
                    ds = [e[0] * t + e[1] for e in d['fixed']]
                else:
                    ds = d['pre'] + [d['mid']] * (d['cnt'][0] * t + d['cnt'][1]) + d['suf']
                ex.append((V, (ds, d['a'][0] * t + d['a'][1], d['b'][0] * t + d['b'][1])))
    out = []
    for m in mods:
        for ca in range(m):
            for cb in range(1, m):
                for cd in range(m):
                    for cn in range(m):
                        def ph(ds, a, b):
                            return (ca * a + cb * b + cd * sum(ds) + cn * len(ds)) % m
                        if all(ph(*x) == ph(*y) for x, y in steps):
                            out.append((m, ca, cb, cd, cn))
    return out, ex


def invariant_verdict(R, E, start, n_at_E):
    """Is the halting exhaustion class excluded by an invariant along the whole run?"""
    invs, ex = find_invariants(R, E)
    if not invs or not E:
        return None, 'no invariant' if not invs else 'no E map'
    p, cls = E
    for (m, ca, cb, cd, cn) in invs:
        def ph(ds, a, b):
            return (ca * a + cb * b + cd * sum(ds) + cn * len(ds)) % m
        p0 = ph(*start)
        # exhaustion configuration K(0^n; 0; V): Phi = cb V + cn n (P empty: n = 0)
        # all rebuilds must restore p0 (checked on samples) and the halting classes must be incompatible
        L = p * m // math.gcd(p, m)
        ok_rebuild = all(ph(*cfg) == p0 for V, cfg in ex if (cb * V + cn * n_at_E) % m == p0)
        if not ok_rebuild:
            continue
        halting = [c for c in range(L) if cls[c % p][0] == 'H' and (cb * c + cn * n_at_E) % m == p0]
        other = [c for c in range(L) if cls[c % p][0] not in ('H', 'K') and (cb * c + cn * n_at_E) % m == p0]
        if not halting and not other:
            return ('Phi=%da+%db+%dsum+%dlen mod %d = %d: every compatible exhaustion rebuilds, rebuild keeps Phi'
                    % (ca, cb, cd, cn, m, p0)), invs
    return None, 'invariants %s not decisive' % invs[:4]


def fit_E2(P, R, n, B0, row=None, tag='', mode=None):
    """exhaustion map in V-terms: probes from K(0^n;0;V) and from the natural predecessor K(0^n;1;b) (V = F0(b)).
    a=0 map is used when it agrees with the composite on the overlap (or the composite is unavailable)."""
    m1, c1 = R['F0']
    if mode == 'a0':
        pat0, E0, _ = fit7.fit_E(P, n, B0)
        return pat0, E0
    if mode == 'a1' and m1 >= 1:
        b0 = max(0, (B0 - c1) // m1)
        pat1, E1b, _ = fit7.fit_E(P, n, b0, a0=1)
        return pat1, fit7.e_to_V(E1b, m1, c1)
    pat0, E0, _ = fit7.fit_E(P, n, B0)
    E1 = None
    pat1 = '-'
    if m1 >= 1:
        b0 = max(0, (B0 - c1) // m1)
        pat1, E1b, _ = fit7.fit_E(P, n, b0, a0=1)
        E1 = fit7.e_to_V(E1b, m1, c1)
    choice = 'a0'
    a1ok = E1 is not None and not any(r[0] in ('T', 'D') for r in E1b[1].values())
    if E0 is None or (E0[0] == 1 and E0[1][0][0] == 'T'):
        if a1ok:
            choice = 'a1'
    elif a1ok:
        # compare on V values in the a1 image
        p0, c0 = E0
        p1, cl1 = E1
        bad = 0
        for V in range(B0 + 5, B0 + 5 + 4 * p0 * p1):
            r1 = cl1[V % p1]
            if r1[0] == 'X':
                continue
            r0 = c0[V % p0]
            if r0[0] != r1[0]:
                bad += 1
        if bad:
            choice = 'disagree'
    if row is not None:
        row['Echoice' + tag] = choice
        row['Epat_a1' + tag] = pat1
    return (pat0 if choice != 'a1' else pat1), (E1 if choice == 'a1' else E0)


def analyse(m, tmpl, args, log):
    t0 = time.time()
    row = {'machine': m, 'tmpl_in': tmpl}
    fits = []
    R = P = None
    cands = list(fit7.variants(tmpl))
    for rc in fit7.recodings(tmpl):
        cands += [x for x in fit7.variants(rc) if x not in cands]
    for tv, absorbed in cands[:12]:
        P = fit7.Prober(m, tv)
        try:
            R = fit7.fit_rules(P)
            row['tmpl'] = tv
            row['absorbed'] = absorbed
            break
        except fit7.FitError as e:
            fits.append('%s: %s' % (tv, e))
            R = None
        except Exception as e:  # noqa
            fits.append('%s: %r' % (tv, e))
            R = None
    row['fit_fail'] = fits
    if R is None:
        row['verdict'] = 'NOFIT'
        row['time'] = round(time.time() - t0, 1)
        return row
    row['rules'] = rules_str(R)
    row['smallB'] = {k: v[:8] for k, v in R['smallB'].items()}
    row['smallD'] = R['smallD'][:6]
    row['excR2'] = R['excR2']
    # literal trace
    ks, end = P.trace(args.steps, args.maxk)
    row['trace_end'] = end
    row['nK'] = len(ks)
    if end and end[0] == 'HALT':
        row['verdict'] = 'LITERAL-HALT'
        row['halt'] = end
        row['time'] = round(time.time() - t0, 1)
        return row
    if not ks:
        row['verdict'] = 'NO-K'
        row['time'] = round(time.time() - t0, 1)
        return row
    bad, exh = lockstep(P, R, ks)
    row['first_K'] = [ks[0][0], ks[0][1][:20], ks[0][2], ks[0][3]]
    row['last_K'] = [ks[-1][0], ks[-1][1][:40], len(ks[-1][1]), ks[-1][2], ks[-1][3]]
    row['lock_bad'] = len(bad)
    row['lock_bad_eg'] = bad[-3:]
    row['lit_exh'] = exh[:12]
    ok, n, nt, miss = fit7.check_random(P, R, n=args.rand)
    row['rand'] = [ok, n, nt]
    row['rand_miss'] = [(c, rule, r) for c, rule, r in miss[:4]]
    # exhaustion map
    start = (ks[-1][1], ks[-1][2], ks[-1][3])
    n0 = len(start[0])
    Es = {}
    for n in ([0] if P.Pempty else [n0]):
        pat, E = fit_E2(P, R, n, 60, row, '')
        patF, EF = fit_E2(P, R, n, 300, mode='a1' if row.get('Echoice') == 'a1' else 'a0')
        Es[n] = (pat, E, patF, EF)
    row['E_pat'] = {n: v[0] for n, v in Es.items()}
    row['E'] = {n: e_struct_str(v[1]) for n, v in Es.items()}
    row['E_far_same'] = {n: (e_struct_str(v[1]) == e_struct_str(v[3])) for n, v in Es.items()}
    Ekey = 0 if P.Pempty else n0
    E = Es[Ekey][1]
    ndep = len(set(e_struct_str(v[1]) for v in Es.values())) > 1
    row['E_ndep'] = ndep
    row['sig'] = signature(R, E)
    # halting events catalogue
    ev = []
    for k, lst in R['smallB'].items():
        hs = [b for b, kind, *_ in lst if kind == 'H']
        if hs:
            ev.append('B%d halts at b=%s' % (k, hs[:6]))
    if E:
        hc = [c for c, r in E[1].items() if r[0] == 'H']
        if hc:
            ev.append('E halts for b mod %d in %s' % (E[0], hc))
        tc = [c for c, r in E[1].items() if r[0] == 'T']
        if tc:
            ev.append('E leaves template for b mod %d in %s' % (E[0], tc))
    row['halt_events'] = ev
    # growth class of the engine
    try:
        ge = eng7.Eng(R, Q=Q1, loose=True)
        if R['F0'][0] == 0:
            growth = 'COUNTER'
        else:
            ds_ = [ge.level_desc(j) for j in range(1, 25)]
            growth = 'POLY' if all(d[0] == 'aff' and d[1] <= 1 for d in ds_) else 'FOMEGA'
            row['levels'] = ','.join('a%d' % d[1] if d[0] == 'aff' else 'g' for d in ds_[:12])
    except Exception as e:  # noqa
        growth = 'ERR %s' % e
    row['growth'] = growth
    # residue rounds
    marker = bool(R.get('MB'))
    row['marker'] = marker
    if not P.Pempty:
        row['MBwhy'] = R.get('MBwhy')
    nE = R.get('nE', 0)
    row['nE'] = nE
    row['mscan'] = R.get('mscan')
    if marker:
        pat0, E0 = fit_E2(P, R, nE, 60, row, '_E0')
        patF0, EF0 = fit_E2(P, R, nE, 300, mode='a1' if row.get('Echoice_E0') == 'a1' else 'a0')
        row['E0_pat'] = pat0
        row['E0'] = e_struct_str(E0)
        row['E0_far_same'] = e_struct_str(E0) == e_struct_str(EF0)
        E = E0
        row['sig'] = signature(R, E)

    def lit(V, n):
        nn = nE if marker else n
        return P.probe([([0] * nn if not P.Pempty else [], 0, V)], N=60000000)[0]
    Ecache = {}

    def Efor(n):
        if P.Pempty or marker:
            return E
        if isinstance(n, tuple):
            if 'huge' not in Ecache:
                md = 'a1' if row.get('Echoice') == 'a1' else 'a0'
                e1 = fit_E2(P, R, 24, 60, mode=md)[1]
                e2 = fit_E2(P, R, 25, 60, mode=md)[1]
                Ecache['huge'] = e1 if (e1 and e_struct_str(e1) == e_struct_str(e2)) else None
            return Ecache['huge']
        if n not in Ecache:
            Ecache[n] = E if n == n0 else fit_E2(P, R, n, 60, mode='a1' if row.get('Echoice') == 'a1' else 'a0')[1]
        return Ecache[n]
    rr = {}
    for Q in (Q1, Q2):
        if E is None:
            rr[Q] = ('NO-E-MAP', [], [], [], None)
            continue
        eng = eng7.Eng(R, Q=Q, JMAX=3000 if Q == Q1 else 1600)
        eng.deadline = time.time() + 300
        try:
            V = eng.value(start[0], start[1], start[2])
            if marker:
                V = eng.staircase(V, len(start[0]))
            v, tr = rounds7.run_rounds(eng, Efor, V, n0=len(start[0]), marker=marker, lit=lit)
        except eng7.EngError as e:
            v, tr = 'ERR@0: %s' % e, []
        except RecursionError:
            v, tr = 'ERR@0: recursion', []
        rr[Q] = (v, tr[:12], eng.flags[:4], eng.precond[:4], eng.period)
    row['rounds'] = {str(Q): rr[Q] for Q in rr}
    # invariant
    if E is not None:
        try:
            iv, det = invariant_verdict(R, E, start, 0 if (P.Pempty or row.get('marker')) else n0)
        except Exception as e:  # noqa
            iv, det = None, 'err %r' % e
        row['invariant'] = iv
        row['inv_detail'] = str(det)[:300]
    # verdict
    v1, v2 = rr[Q1][0], rr[Q2][0]
    flags1 = rr[Q1][2] if len(rr[Q1]) > 2 else []
    flags2 = rr[Q2][2] if len(rr[Q2]) > 2 else []
    if v1.startswith('HALT@') or v2.startswith('HALT@'):
        verdict = 'HALT-REACHED(%s/%s)' % (v1[:30], v2[:30])
    elif any(x.startswith(('CLASS-DEPENDENT', 'HALT-SOME')) for x in (v1, v2)):
        verdict = 'CLASS-DEPENDENT(%s | %s)' % (v1[:60], v2[:60])
    elif v1.startswith('LOOP') and not flags1:
        verdict = 'NEVER-HALTS(residue)'
        if v2.startswith('LOOP') and not flags2:
            verdict += '+Q2'
        elif not v2.startswith(('ERR', 'UNSETTLED')):
            verdict += '+Q-CONFLICT(%s)' % v2[:40]
    elif v2.startswith('LOOP') and not flags2:
        verdict = 'NEVER-HALTS(residue Q2 only)'
    else:
        verdict = 'UNSETTLED(%s | %s)' % (v1[:90], v2[:60])
        if flags1:
            verdict += '+FLAGS'
    if row.get('growth') in ('COUNTER', 'POLY') and not verdict.startswith('HALT'):
        verdict = 'NOT-RECORD-CLASS(%s) ' % row['growth'] + verdict
    if row.get('invariant') and not verdict.startswith('HALT'):
        verdict += '+INV'
    if bad:
        verdict += '+LOCKMISS%d' % len(bad)
    if miss:
        verdict += '+RANDMISS%d' % len(miss)
    row['E_used_n'] = sorted(str(k) for k in Ecache)
    if ndep and not row.get('marker'):
        verdict += '+E-NDEP'
    if not P.Pempty and not marker and R.get('mscan') and 'S' in R['mscan']:
        verdict += '+SHRINK-UNMODELLED(%s)' % R['mscan']
    if E is not None and not all(row['E_far_same'].values()):
        verdict += '+E-FAR-DIFF'
    row['verdict'] = verdict
    row['time'] = round(time.time() - t0, 1)
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pool')
    ap.add_argument('out')
    ap.add_argument('--only')
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--shard', default='0/1')
    ap.add_argument('--steps', type=int, default=300000000)
    ap.add_argument('--maxk', type=int, default=3000)
    ap.add_argument('--rand', type=int, default=80)
    args = ap.parse_args()
    done = set()
    if os.path.exists(args.out):
        for ln in open(args.out, encoding='utf-8'):
            try:
                done.add(json.loads(ln)['machine'])
            except Exception:  # noqa
                pass
    si, sn = map(int, args.shard.split('/'))
    rows = []
    for i, ln in enumerate(open(args.pool, encoding='utf-8')):
        f = ln.rstrip('\n').split('\t')
        if len(f) < 2 or f[0] == 'machine':
            continue
        if args.only and f[0] != args.only:
            continue
        rows.append((f[0], f[1]))
    rows = [r for j, r in enumerate(rows) if j % sn == si and r[0] not in done]
    if args.limit:
        rows = rows[:args.limit]
    sys.setrecursionlimit(100000)
    with open(args.out, 'a', encoding='utf-8', newline='\n') as fo:
        for i, (m, t) in enumerate(rows):
            try:
                row = analyse(m, t, args, None)
            except Exception as e:  # noqa
                row = {'machine': m, 'tmpl_in': t, 'verdict': 'ERROR', 'err': traceback.format_exc()[-800:]}
            fo.write(json.dumps(row, default=str) + '\n')
            fo.flush()
            print('%d/%d %s %s %.0fs' % (i + 1, len(rows), m, row.get('verdict'), row.get('time', 0)), flush=True)


if __name__ == '__main__':
    main()
