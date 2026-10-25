"""pswitch.py: second-template analysis for reb7 rows whose exhaustion leaves the template (T).
  python pswitch.py IN.jsonl[,IN2] OUT.jsonl [--only M]
For each row with a T exhaustion at round 1:
  1. ffree.exe: literal run from the exhaustion K_T(0^n; a0; b) with a FREE prefix -> prefix P' of the first
     K-moment after the exhaustion (the rebuilt configuration may absorb or create an outer part).
  2. T' = T with P = P'; fit T' rules (fit7) incl. marker scan; cross exhaustion map T -> T' (xprobe.exe, classes).
  3. Rounds: V1 = exhaustion value in T (engine of T) -> class -> rebuilt configuration in T' -> value in T' (engine
     of T') -> T' exhaustion map -> ... (run_rounds with T' engine).
Verdicts as reb7 (NEVER-HALTS(residue,switch) / HALT-REACHED / CLASS-DEPENDENT / UNSETTLED)."""
import idle  # noqa: F401
import json
import os
import subprocess
import sys
import time

import fit7
import eng7
import rounds7
import reb7

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
    p = subprocess.run([FFREE, m] + ta(t) + [str(N), '3'], input=inp, capture_output=True, text=True,
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


def analyse(r):
    t0 = time.time()
    m, t = r['machine'], r['tmpl']
    row = {'machine': m, 'tmpl': t}
    P = fit7.Prober(m, t)
    R = fit7.fit_rules(P)
    ks, end = P.trace(300000000, 3000)
    start = (ks[-1][1], ks[-1][2], ks[-1][3])
    marker = bool(R.get('MB'))
    if marker:
        n = R.get('nE', 0)
    elif P.Pempty:
        n = 0
    else:
        n = len(start[0])
    a0 = 1 if (r.get('Echoice') == 'a1' or r.get('Echoice_E0') == 'a1') else 0
    ds = [0] * n if not P.Pempty else []
    lines = ffree_first(m, t, ds, a0, 61)
    row['ffree'] = lines[:3]
    k = [l for l in lines if l.startswith('K')]
    if not k:
        row['verdict'] = 'UNSETTLED(no K-moment after the exhaustion even with a free prefix: %s)' % (lines[-1:] or ['?'])
        return row
    pref = k[0].split()[2][2:]
    P2s = unrle(pref)
    T = fit7.parse_template(t)
    T2 = dict(T)
    T2['P'] = P2s if P2s else '-'
    if P2s and P2s[0] != '1':
        row['verdict'] = 'UNSETTLED(free prefix starts with 0: %s)' % pref
        return row
    t2 = fit7.tstr(T2)
    row['tmpl2'] = t2
    P2 = fit7.Prober(m, t2)
    try:
        R2 = fit7.fit_rules(P2)
    except fit7.FitError as e:
        row['verdict'] = 'UNSETTLED(T2 nofit: %s)' % e
        return row
    row['rules2'] = reb7.rules_str(R2)
    marker2 = bool(R2.get('MB'))
    row['marker2'] = marker2
    row['mscan2'] = R2.get('mscan')
    # cross exhaustion map T -> T2 (classes of V; a0 = 1 composite converted like reb7.fit_E2)
    m1, c1 = R['F0']
    if a0 == 1:
        b0 = max(0, (60 - c1) // m1)
        pat, Eb, _ = fit7.fit_E(P, n, b0, a0=1, probe=lambda cf: xprobe(m, t, t2, cf), out_pempty=P2.Pempty)
        E12 = fit7.e_to_V(Eb, m1, c1)
    else:
        pat, E12, _ = fit7.fit_E(P, n, 60, probe=lambda cf: xprobe(m, t, t2, cf), out_pempty=P2.Pempty)
    row['E12_pat'] = pat
    row['E12'] = reb7.e_struct_str(E12)
    if E12 is None:
        row['verdict'] = 'UNSETTLED(cross map not affine: %s)' % pat
        return row
    # T2 exhaustion map
    nE2 = R2.get('nE', 0) if marker2 else None

    def E2for(nn):
        if marker2:
            return E2
        if P2.Pempty:
            return E2
        if isinstance(nn, tuple):
            e1 = reb7.fit_E2(P2, R2, 24, 60)[1]
            e2 = reb7.fit_E2(P2, R2, 25, 60)[1]
            return e1 if (e1 and reb7.e_struct_str(e1) == reb7.e_struct_str(e2)) else None
        return reb7.fit_E2(P2, R2, nn, 60)[1]
    if marker2 or P2.Pempty:
        _, E2 = reb7.fit_E2(P2, R2, nE2 if marker2 else 0, 60)
        row['E2'] = reb7.e_struct_str(E2)
    else:
        E2 = None
    rr = {}
    for Q in (Q1, Q2):
        e1 = eng7.Eng(R, Q=Q, JMAX=3000 if Q == Q1 else 1600)
        e2 = eng7.Eng(R2, Q=Q, JMAX=3000 if Q == Q1 else 1600)
        try:
            V = e1.value(start[0], start[1], start[2])
            if marker:
                V = e1.staircase(V, len(start[0]))
            br = rounds7.step_world(e2, lambda nn: E12, V, n, False, None)
            outs = []
            for kind, V2, n2, note in br:
                if kind != 'K':
                    outs.append('%s(%s)' % (kind, note))
                    continue
                # V2 was computed with e2's engine on the T2 list (step_world uses eng=e2 for value) ; staircase in T2
                if marker2:
                    V2 = e2.staircase(V2, n2)
                v, tr = rounds7.run_rounds(e2, E2for, V2, n0=n2 if not isinstance(n2, tuple) else n2,
                                           marker=marker2, lit=None)
                outs.append(v)
            rr[Q] = (outs, e1.flags[:3] + e2.flags[:3], e1.precond[:2] + e2.precond[:2])
        except eng7.EngError as e:
            rr[Q] = (['ERR: %s' % e], [], [])
        except RecursionError:
            rr[Q] = (['ERR: recursion'], [], [])
    row['rounds'] = {str(Q): rr[Q] for Q in rr}
    o1 = rr[Q1][0]
    if any(x.startswith('HALT') for x in o1) or any(x.startswith('H(') for x in o1):
        v = 'HALT-REACHED(switch: %s)' % o1
    elif o1 and all(x.startswith('LOOP') for x in o1) and not rr[Q1][1]:
        v = 'NEVER-HALTS(residue,switch)'
        if all(x.startswith('LOOP') for x in rr[Q2][0]):
            v += '+Q2'
    elif any(x.startswith(('CLASS-DEPENDENT', 'HALT-SOME')) for x in o1):
        v = 'CLASS-DEPENDENT(switch: %s)' % o1
    else:
        v = 'UNSETTLED(switch: %s)' % [x[:80] for x in o1]
    row['verdict'] = v
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
            rq = str(r.get('rounds', {}).get('80640', ['-'])[0]) if r.get('rounds') else ''
            if ("'T'" in rq or rq.startswith('T@')) and r['machine'] not in done and (not only or r['machine'] == only):
                rows.append(r)
    sys.setrecursionlimit(100000)
    with open(out, 'a', newline='\n') as fo:
        for r in rows:
            try:
                row = analyse(r)
            except Exception as e:  # noqa
                import traceback
                row = {'machine': r['machine'], 'verdict': 'ERROR', 'err': traceback.format_exc()[-600:]}
            fo.write(json.dumps(row, default=str) + '\n')
            fo.flush()
            print(r['machine'], row.get('verdict'), row.get('tmpl2'), flush=True)


if __name__ == '__main__':
    main()
