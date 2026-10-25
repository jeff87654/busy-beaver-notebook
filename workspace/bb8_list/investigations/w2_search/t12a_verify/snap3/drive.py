"""Drive H14 abstractly from the Coq-proved round-1 end B-form  Bf (FarE k1) [0, 1^w | f]  (n1's HALT_B start).
python drive.py [maxstages] [logfile]
env: MREP (rep modulus, default 840), GROW (rank spacing), MAXS (literal step cap), START=r1 (default)"""
import sys, time, os
from absim import *
import absim

FARE_NEAR = [0,0,1,0,0,1,0,0,1,0,0,1,0,0,1,1,1,1,0,1,0,0,0,0,0,1,0,0,1,0,1,0,1,0,1,0,1,0,1,0,1,1,0,1]
TAIL = ''.join(map(str, reversed(FARE_NEAR)))


def round1_end():
    """atoms k1, w, f with exact residues (from the Coq chain: T = arrow 37 2 3, JJ = (3T-13)/7, k1 = 4JJ-3,
    depth n_JJ = 34 + JJ*(4u+2), w = n_JJ + 2u, f = U-output, u = (phi-1)/3)"""
    mm = MB // 9
    T7 = tau(7 * 3 * mm)                    # T mod 21mm (T is a tall tower of 2s)
    JJ = ((3 * T7 - 13) % (21 * mm))
    assert JJ % 7 == 0
    JJ = (JJ // 7) % (3 * mm)
    k1 = (4 * JJ - 3) % (3 * mm)
    phi3 = stable_phi(3 * mm)
    u = ((phi3 - 1) // 3) % mm
    nJJ = (34 + JJ * (4 * u + 2)) % mm
    w = (nJJ + 2 * u) % mm
    f = stable_phi(mm)
    K = new_atom('k1', k1, mm, rank=1000, note='round-1 far run 4JJ-3')
    W = new_atom('w', w, mm, rank=1001, note='round-1 end depth')
    F = new_atom('f', f, mm, rank=1002, note='round-1 end acc')
    far = group(tokens('10101' + TAIL))
    assert far[0] == ('t', 2, 1)
    far = [('t', Val(2), K)] + [(r[0],) + tuple(Val(x) if not isinstance(x, tuple) else x for x in r[1:]) for r in far[1:]]
    runs = norm(far + [('t', Val(0), Val(1)), ('t', Val(1), W), ('t', Val(0), Val(1)), ('t', F, Val(1))])
    return runs, dict(k1=K, w=W, f=F, JJmod=JJ, k1mod=k1)




def _fields(runs):
    out = []
    for r in runs:
        if r[0] == 'R':
            out.append(('R', r[1]))
            out.append(Val.of(r[2]))
        elif r[0] == 't':
            out.append('t'); out.append(Val.of(r[1])); out.append(Val.of(r[2]))
        else:
            out.append('z'); out.append(Val.of(r[1]))
    return out


def loop_macro(h3, margin=30):
    """three consecutive literal outputs with identical shape and constant per-field integer deltas -> jump J steps"""
    a, b, c = [_fields(x) for x in h3]
    if not (len(a) == len(b) == len(c)):
        return None
    deltas = []
    for x, y, z in zip(a, b, c):
        if not isinstance(x, Val):
            if not (x == y == z):
                return None
            deltas.append(None)
            continue
        d1, d2 = y - x, z - y
        if not (d1.isconst() and d2.isconst() and d1 == d2):
            return None
        deltas.append(d1.ival())
    dec = [i for i, dl in enumerate(deltas) if dl is not None and dl < 0]
    if len(dec) != 1 or not c[dec[0]].huge():
        return None
    i = dec[0]; s = -deltas[i]; v = c[i]
    rem = margin * s + (v - margin * s).res(s)
    J = (v - rem).div(s)
    new = [((x + J * dl) if dl else x) if isinstance(x, Val) else x for x, dl in zip(c, deltas)]
    # rebuild runs
    out = []; k = 0
    for r in h3[2]:
        if r[0] == 'R':
            out.append(('R', r[1], new[k + 1])); k += 2
        elif r[0] == 't':
            out.append(('t', new[k + 1], new[k + 2])); k += 3
        else:
            out.append(('z', new[k + 1])); k += 2
    return norm(out), J, s

TRAJ = []
LITHIST = []
LASTPER = {}


def drive(runs, maxst=200, log=print, stop=None):
    st = len(TRAJ)
    while st < maxst:
        st += 1
        TRAJ.append(runs)
        if os.environ.get('PKL') and st % 1 == 0:
            import pickle
            try:
                pickle.dump(dict(TRAJ=TRAJ, ATOMS=ATOMS), open(os.environ['PKL'] + '.tmp', 'wb'))
                os.replace(os.environ['PKL'] + '.tmp', os.environ['PKL'])
            except Exception:
                pass
        pm = per_match(runs)
        if pm is not None and pm[0] and os.environ.get('TRUSTPREFIX') == show(pm[0]) and prefix_key(pm[0]) not in absim.PREFIX_OK:
            absim.PREFIX_OK.add(prefix_key(pm[0]))
            log('%4d prefix %s trusted (validated literally in the previous run, c13a.log stage 20)' % (st, show(pm[0])))
        if pm is not None and pm[0]:
            key = prefix_key(pm[0])
            if key in LASTPER:
                k0, m0 = LASTPER[key]
                if pm[1] == k0 + 4 and pm[2] == m0 - 14 and key not in absim.PREFIX_OK:
                    absim.PREFIX_OK.add(key)
                    log('%4d prefix period validated literally (k+4, m-14, prefix unchanged): PERIOD macro enabled for prefix %s' % (st, show(pm[0])))
            LASTPER[key] = (pm[1], pm[2])
        if is_bform(runs):
            p = period_macro(runs)
            if p and p[0] == 'period':
                runs = p[1]
                log('%4d PERIOD J=%r r=%s  -> %s' % (st, p[2]['J'], p[2]['r'], show(runs)))
                LITHIST.clear()
                continue
            if p and p[0] == 'noinv':
                log('%4d (Per form but no PERIOD macro: %s)' % (st, p[1]))
            c = clr(runs)
            if c and c[0] == 'clr':
                runs = c[1]
                log('%4d CLR d=%r n=%r A=%r -> new A %r  | %s' % (st, c[2]['d'], c[2]['n'], c[2]['A'], c[2]['newA'], show(runs)))
                LITHIST.clear()
                if stop and stop(runs):
                    return 'STOP', runs, None, None
                continue
            if c and c[0] == 'noclr-A':
                log('%4d (CLR shape but A != 1 mod 3)' % st)
        if os.environ.get('REATOM'):
            runs, ch = reatomize(runs, int(os.environ.get('REATOM')), log)
        kind, out, info = literal_stage(runs)
        if kind == 'B' and os.environ.get('SIGNCHECK'):
            def mixed(v):
                v = Val.of(v)
                big = [c for a, c in v.co.items() if ATOMS[a].get('tier', 'real') == 'real']
                return any(c > 0 for c in big) and any(c < 0 for c in big)
            bad = [r for r in out for x in r[1:] if not isinstance(x, tuple) and mixed(x)]
            if bad:
                log('      sign check: mixed-sign value %s -> re-running this stage with geo spacing' % (bad[0],))
                old = (absim.REPMODE, absim.GROW)
                absim.REPMODE, absim.GROW = 'geo', int(os.environ.get('SIGNGROW', 3))
                try:
                    kind, out, info = literal_stage(runs)
                finally:
                    absim.REPMODE, absim.GROW = old
                log('      geo result: %s' % (show(out)[:300] if out else kind))
        if kind == 'B':
            runs = out
            LITHIST.append(runs)
            del LITHIST[:-3]
            if len(LITHIST) == 3:
                lm = loop_macro(LITHIST)
                if lm:
                    log('%4d LIT steps=%s t=%.1fs -> %s' % (st, info['steps'][0], info['time'], show(runs)))
                    runs = lm[0]
                    log('%4d LOOP macro: J=%r repetitions of the last literal rewrite (step %d on the decreasing field) -> %s' % (st, lm[1], lm[2], show(runs)))
                    LITHIST.clear()
                    continue
            log('%4d LIT steps=%s t=%.1fs len=%s lo=%r -> %s' % (st, info['steps'][0], info['time'], info['lens'][0], info['lofit'], show(runs)))
        elif kind == 'H':
            log('%4d HALT state %s reads %s, steps=%s; tape %s' % (st, info['q'], info['sym'], info['steps'], show(out)))
            return 'HALT', runs, out, info
        else:
            log('%4d TIMEOUT steps=%s lens=%s' % (st, info['steps'], info['lens']))
            return 'TIMEOUT', runs, None, info
        if stop and stop(runs):
            return 'STOP', runs, None, None
    return 'MAX', runs, None, None


if __name__ == '__main__':
    maxst = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    runs, at = round1_end()
    if os.environ.get('RESUME'):
        import pickle, vals
        fn, idx = os.environ['RESUME'].split(':')
        dd = pickle.load(open(fn, 'rb'))
        vals.ATOMS.clear(); vals.ATOMS.update(dd['ATOMS']); vals._next[0] = max(dd['ATOMS']) + 1
        runs = dd['TRAJ'][int(idx) - 1]
        for v in vals.ATOMS.values():
            if 'tier' not in v:
                v['tier'] = 'real'; v['rank'] = v['rank'] + 1000 if v['rank'] < 1000 else v['rank']
        TRAJ.extend(dd['TRAJ'][:int(idx) - 1])
        print('RESUME from', fn, 'stage', idx)
    print('MREP', MREP, 'GROW', GROW, 'k1 mod 8640 =', at['k1mod'] % 8640, 'k1 mod 3 =', at['k1mod'] % 3)
    for a, v in ATOMS.items():
        print('  atom', v['name'], 'res mod 2520 =', v['res'] % 2520, 'mod MREP =', v['res'] % MREP, v['note'])
    print('start', show(runs))
    sys.stdout.flush()

    def lg(s):
        print(s, flush=True)
    import pickle
    try:
        r = drive(runs, maxst, lg)
        print('END', r[0])
    finally:
        pickle.dump(dict(TRAJ=TRAJ, ATOMS=ATOMS), open(os.environ.get('PKL', 'traj.pkl'), 'wb'))
