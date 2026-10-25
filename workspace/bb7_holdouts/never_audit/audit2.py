"""audit_f1.py: independent audit of single-accumulator digit-list machines in v-coding
   K-config = [d_1..d_n, A] + TF   (TF = fixed trailing runs, e.g. [2] or [1] or []), K event (Q, right end), z = Z.
usage: python audit_f1.py MACHINE Q SIDE TF(comma list or -) Z [literal_steps]      (env NCL, LIGHT)
Step 1 MEASURES the rules by symsim (sound symbolic execution, symbolic A and digits):
   D_k : [.., y+1, 0^k, A] -> [.., y, new_k(A)...]   (k = 0 is the plain decrement)
Step 2 re-checks every probe (left contexts, small y, A classes) against the measured base rule.
Step 3 exhaustion [X]+TF per class X = r mod 720 (r < NCL), symbolic (sound for X >= 1000 in the class): HALT / rebuild.
Step 4 literal lockstep (my rule engine vs the literal K-trace), borrow margins.
Step 5 invariant search: wD*sum(d) + wA*A mod m (m = 2,3,4,6) kept by every measured rule and by the literal run;
       then: which exhaustion classes it allows, whether any of them halts, whether the rebuild restores it.
"""
import sys, idle_guard
from fam import *
from coding import VCoding, U10Coding, ChampCoding
CODINGS = {'V': VCoding(), 'U10': U10Coding(), 'U10s2': U10Coding(2), 'U110': U10Coding(1, 2), 'C1': ChampCoding()}

def audit(m0, Q, SIDE, TF, Z, LSTEPS=10**9, NCL=120, light=False, out=print, coding='V'):
    C = CODINGS[coding]
    R = {'machine': m0, 'coding': coding}
    m = mirror(m0) if SIDE == 'L' else m0
    nT = len(TF)
    def dec(v):
        try:
            d, tf = C.decode(v, nT)
        except Exception:
            return None
        if len(tf) != nT: return None
        for e, t in zip(tf, TF):
            if isinstance(e, tuple): return None
            if isinstance(e, Lin):
                if not e.isconst() or e.const() != t: return None
            elif e != t: return None
        if not d: return None
        return d
    def isK(v, z):
        return z == Z and dec(v) is not None
    def kstep(v0, prove, budget, tlimit, n=1):
        tp = C.encode(v0, TF, Z, Q)
        for NS in (3, 12, 48, 200, 800):
            verdict, st, fin, raw = run_sym(m, Q, tp, stopn=NS, mg=720, hlb=1000, budget=budget, tlimit=tlimit, prove=prove)
            ks = []
            for a, t, sd in st:
                try: qq, vv, zz, rb = stop_v(t)
                except Exception: continue
                if zz == Z:
                    d = dec(vv)
                    if d is not None:
                        ks.append((d, sd))
                        if len(ks) >= n: return 'K', ks
            if verdict != 'STOP': return verdict, ks
        return verdict, ks
    def split(d): return d[:-1], d[-1]
    out('# machine %s side %s oriented %s K %s TF %s z %d' % (m0, SIDE, m, Q, TF, Z))
    def probe_sym(v0):
        r, ks = kstep(v0, coding != 'V', 300000, 30)
        if r != 'K': return r, None, None
        d1, sd = ks[0]; env = symenv(sd)
        names = sorted(env, key=lambda s: int(s[1:])); it = iter(names); sub = []
        for e in v0: sub.append(Lin({next(it): 1}) if isinstance(e, str) else Lin.c(e))
        return 'K', sub, expand(d1)
    def probe_exact(v0):
        """fallback: exact (literal, chain-step accelerated) runs at large values, affine fit per symbol, verified"""
        syms = [i for i, e in enumerate(v0) if isinstance(e, str)]
        def val(i, bump): return 1200 + int(v0[i][1:]) + (720 if bump else 0)
        def once(bumps):
            vv = [val(i, i in bumps) if i in syms else e for i, e in enumerate(v0)]
            r, ks = kstep(vv, False, 3000000, 60)
            if r != 'K': return None
            return [int(x.const()) if isinstance(x, Lin) else x for x in expand(ks[0][0])]
        base = once(set())
        if base is None: return 'EXACT-FAIL', None, None
        names = {i: 'X%d' % j for j, i in enumerate(syms)}
        coef = {}
        for i in syms:
            b = once({i})
            if b is None or len(b) != len(base): return 'EXACT-SHAPE', None, None
            coef[i] = [Fr(x - y, 720) for x, y in zip(b, base)]
        res = []
        for p in range(len(base)):
            e = Lin.c(base[p])
            for i in syms: e = e + Lin({names[i]: coef[i][p]}) - coef[i][p] * val(i, False)
            res.append(e)
        chk = once(set(syms))       # verification point: all symbols bumped
        if chk is None or len(chk) != len(base): return 'EXACT-SHAPE', None, None
        for p in range(len(base)):
            if res[p].ev({names[i]: val(i, True) for i in syms}) != chk[p]: return 'EXACT-NONAFFINE', None, None
        sub = [Lin({names[i]: 1}) if i in syms else Lin.c(e) for i, e in enumerate(v0)]
        return 'K', sub, res
    DEC = {}
    def probe(left, y, k, Ar, cdec=None):
        v0 = left + [y] + [0] * k + [Ar]
        def shape_ok(sub, got):
            i = len(left)
            if not got: return False
            cs = [cdec] if cdec else [1, 2, 3]
            if i == 0 and any((sub[0] - c) == 0 for c in cs): return True
            if len(got) <= i: return False
            return all((got[j] - sub[j]) == 0 for j in range(i)) and any((got[i] - (sub[i] - c)) == 0 for c in cs)
        r, sub, got = probe_sym(v0)
        if r != 'K' or not shape_ok(sub, got):
            r2, sub2, got2 = probe_exact(v0)
            if r2 == 'K' and shape_ok(sub2, got2):
                FALLBACK.append(k); return v0, 'K', sub2, got2
        return v0, r, sub, got
    FALLBACK = []
    KS = list(range(0, 7)) + [12, 20] if light else (list(range(0, 9)) + [12, 20, 30] if os.environ.get('MED') else list(range(0, 13)) + [20, 30])
    rules = {}
    for k in KS:
        v0, r, sub, got = probe([], 'H3', k, 'H0')
        if r != 'K': out('RULE k=%d: %s' % (k, r)); rules[k] = r; continue
        y = sub[0]; rest = got
        cc = [c for c in (1, 2, 3) if rest and (rest[0] - (y - c)) == 0]
        if not cc: out('RULE k=%d unexpected head %s' % (k, vshow(got))); rules[k] = 'odd'; continue
        DEC[k] = cc[0]
        rules[k] = rest[1:]
        out('RULE k=%2d: [y+%d,0^%d,A] -> [y, %s]' % (k, DEC[k], k, vshow(rest[1:])))
    R['exact_fallback'] = sorted(set(FALLBACK))
    if FALLBACK: out('exact (literal large-value) fallback used for k in %s' % sorted(set(FALLBACK)))
    R['rule0'] = vshow(rules[0]) if isinstance(rules.get(0), list) else str(rules.get(0))
    R['rule1'] = vshow(rules[1]) if isinstance(rules.get(1), list) else str(rules.get(1))
    R['rule5'] = vshow(rules[5]) if isinstance(rules.get(5), list) else str(rules.get(5))
    def baseA(ref):
        b = None
        for e in ref:
            for kk in e.d:
                if kk: b = kk
        return b
    def subst(e, Aname, Aval):
        r = Lin.c(e.d.get('', 0))
        for kk, c in e.d.items():
            if kk == '': continue
            r = r + Aval * c if kk == Aname else r + Lin({kk: c})
        return r
    bad = 0; n = 0
    for k in KS:
        for y in ([1, 'H3'] if light else [1, 2, 'H3']):
            for left in ([[], ['H5']] if light else ([[], [3], ['H5']] if os.environ.get('MED') else [[], [3], ['H5'], [1, 0]])):
                if left == [1, 0] and k > 6: continue
                for Ar in (['H0', 'H1'] if light or os.environ.get('MED') else ['H0', 'H1', 'H2']):
                    n += 1
                    if isinstance(y, int) and y < DEC.get(k, 1): continue
                    v0, r, sub, got = probe(left, y, k, Ar, DEC.get(k))
                    ref = rules.get(k)
                    if r != 'K' or not isinstance(ref, list):
                        if r != 'K' and isinstance(ref, list): out('PROBE %s %s' % (v0, r)); bad += 1
                        continue
                    def predict(sub):
                        d, A = sub[:-1], sub[-1]
                        yy = d[len(left)]; pre = d[:len(left)]
                        bA = baseA(ref)
                        pred = pre + [yy - DEC.get(k, 1)] + [subst(e, bA, A) for e in ref]
                        while pred and pred[0] == 0: pred = pred[1:]
                        return pred
                    pred = predict(sub)
                    ok = len(pred) == len(got) and all((a - b) == 0 for a, b in zip(pred, got))
                    if not ok:      # symbolic run may have skipped a K-moment through a proved rule: re-measure exactly
                        r2, sub2, got2 = probe_exact(v0)
                        if r2 == 'K':
                            pred2 = predict(sub2)
                            ok = len(pred2) == len(got2) and all((a - b) == 0 for a, b in zip(pred2, got2))
                            if ok: FALLBACK.append(k)
                            else: got, pred = got2, pred2
                    if not ok:
                        bad += 1
                        if bad <= 8: out('MISMATCH %s got %s pred %s' % (v0, vshow(got), vshow(pred)))
    out('symbolic probes %d mismatches %d' % (n, bad))
    R['probes'] = n; R['probe_bad'] = bad
    # exhaustion classes
    hc = []; rbf = collections.Counter(); und = []; reb = {}
    for r_ in range(NCL):
        r, ks = kstep(['H%d' % r_], True, 400000, 60)
        if r == 'HALT': hc.append(r_)
        elif r == 'K': rbf[vshow(ks[0][0])] += 1; reb[r_] = (ks[0][0], symenv(ks[0][1]))
        else: und.append((r_, r))
    out('EXHAUSTION [X]+TF, X = r mod 720, r < %d: HALT classes %s (%d) not-K %s' % (NCL, hc[:40], len(hc), und[:5]))
    for f, c in rbf.most_common(4): out('   rebuild %d x %s' % (c, f))
    R['halt_classes'] = hc; R['exh_notK'] = und; R['rebuild'] = [f for f, c in rbf.most_common(3)]
    # literal lockstep
    AFF = {}
    def nxt(v):
        d, A = split(v)
        k = 0
        while k < len(d) and d[len(d) - 1 - k] == 0: k += 1
        if k == len(d): return 'E'
        ref = rules.get(k)
        if not isinstance(ref, list):
            # extrapolate from the measured family when k not probed: refill/tail pattern of k-1 and k-2
            return None
        if k not in AFF:
            bA = baseA(ref)
            AFF[k] = [(int(e.d.get(bA, 0)) if bA else 0, int(e.d.get('', 0))) for e in ref]
        y = d[len(d) - 1 - k]; pre = d[:len(d) - 1 - k]
        if y < DEC.get(k, 1): return None
        o = pre + [y - DEC.get(k, 1)] + [ca * A + cb for ca, cb in AFF[k]]
        while o and o[0] == 0: o = o[1:]
        return o
    tr, tail = lit_k(m, Q, LSTEPS)
    K = []
    for s, v, z in tr:
        if z != Z: continue
        dd = dec(v)
        if dd is not None: K.append((s, [int(x.const()) if isinstance(x, Lin) else x for x in dd]))
    out('literal K-configs %d in %d steps; %s first %s' % (len(K), LSTEPS, tail[:40], K[:2]))
    miss = 0; nE = 0; ex = []; skip = 0; margins = {}; DELTAS = set()
    for (s0, v0), (s1, v1) in zip(K, K[1:]):
        p = nxt(v0)
        if p is None: skip += 1; continue
        if p == 'E': nE += 1; ex.append((s0, split(v0)[1], len(v1))); continue
        DELTAS.add((sum(v1[:-1]) - sum(v0[:-1]), v1[-1] - v0[-1]))
        if p != v1:
            miss += 1
            if miss <= 5: out('LOCK MISS at %d %s -> %s pred %s' % (s0, v0[-8:], v1[-8:], p[-8:]))
        d, A = split(v0); k = 0
        while k < len(d) and d[len(d) - 1 - k] == 0: k += 1
        if k: margins[k] = min(margins.get(k, 10**18), A)
    out('lockstep pairs %d misses %d skipped %d exhaustions(step,X,next len) %s' % (len(K) - 1, miss, skip, ex[:6]))
    out('min A at borrows over k zeros: %s' % dict(sorted(margins.items())[:12]))
    R.update(nK=len(K), lock_miss=miss, lock_skip=skip, lit_exh=ex[:6], margins=dict(sorted(margins.items())[:6]))
    # invariants
    def feats(v):
        d, A = split(v); return (sum(d), A)
    cands = []
    for mm in (2, 3, 4, 6):
        for wD in range(mm):
            for wA in range(mm):
                if (wD, wA) == (0, 0): continue
                ok = True
                for dS, dA in DELTAS:
                    if (wD * dS + wA * dA) % mm: ok = False; break
                if not ok: continue
                for k, ref in rules.items():
                    if not isinstance(ref, list): continue
                    newd, newA = ref[:-1], ref[-1]
                    bA = baseA(ref); Aval = Lin({bA: 1}) if bA else Lin.c(0)
                    delta = wD * (-DEC.get(k, 1) + sum(newd, Lin.c(0))) + wA * (newA - Aval)
                    for kk, c in delta.d.items():
                        if c.denominator != 1 or int(c) % mm: ok = False
                    if not ok: break
                if ok: cands.append((mm, wD, wA))
    out('linear invariants (m, wD, wA) of wD*sum(d)+wA*A mod m: %s' % cands[:12])
    def lin_at(e, env, rep):
        if isinstance(e, int): return Fr(e)
        return e.ev({k: env[k] + 720 * rep for k in env})
    hset = set(hc); verdict = None; invs = []
    for (mm, wD, wA) in cands:
        vals = set((wD * feats(v)[0] + wA * feats(v)[1]) % mm for s, v in K[5:])
        if len(vals) != 1: continue
        pv = vals.pop()
        allowed = [r_ for r_ in range(NCL) if (wA * r_) % mm == pv]
        bad_h = [r_ for r_ in allowed if r_ in hset]
        rb_ok = True
        for r_ in allowed:
            if r_ not in reb: continue
            v1, env = reb[r_]
            tot = Fr(0); vv = list(v1)
            if isinstance(vv[-1], tuple): vv = vv[:-1] + [('blk', vv[-1][1], vv[-1][2] - 1)] + list(vv[-1][1])
            dpart, Ap = vv[:-1], vv[-1]
            for e in dpart:
                if isinstance(e, tuple): tot += lin_at(e[2], env, 1000) * sum(lin_at(x, env, 1000) for x in e[1])
                else: tot += lin_at(e, env, 1000)
            val = (wD * tot + wA * lin_at(Ap, env, 1000)) % mm
            if val != pv: rb_ok = False
        out('   invariant %s = %d on the run; allowed exhaustion classes %s...; halting among them: %s; rebuild keeps it: %s'
            % ((mm, wD, wA), pv, allowed[:6], bad_h[:6], rb_ok))
        invs.append(((mm, wD, wA), pv, bool(bad_h), rb_ok))
        if not bad_h and rb_ok and hc and not [k for k in KS if not isinstance(rules.get(k), list)]: verdict = 'CONFIRMED(invariant %s=%d excludes halting exhaustion classes)' % ((mm, wD, wA), pv)
    missing = [k for k in KS if not isinstance(rules.get(k), list)]
    R['rules_missing'] = missing
    if missing:
        verdict = None
    if not hc and not und and bad == 0 and not missing: verdict = verdict or 'CONFIRMED(no halting exhaustion class r<%d; rules halt-free in probes)' % NCL
    # last-borrow route: after the last borrow before an exhaustion only plain decrements happen, so A_E lies in the
    # orbit (mod 720) of A' (set by a borrow whose tail digits are all zero) under the decrement map D.
    if verdict is None and hc and not missing and bad == 0:
        try:
            r0 = rules[0]; bA = baseA(r0); Da, Db = int(r0[-1].d.get(bA, 0)) if bA else 0, int(r0[-1].d.get('', 0))
            starts = set(); okLB = True
            for k in KS:
                if k == 0: continue
                new = rules[k]
                if all((e == 0) for e in new[1:-1]):     # tail digits all zero: can be the last borrow
                    ap = new[-1]; b2 = baseA([ap])
                    if b2: okLB = False; break           # A' depends on A: no conclusion
                    starts.add(int(ap.const()) % 720)
            # a rebuild also sets A (its new A' starts a run of plain decrements if the rebuilt list has one digit)
            for r_, (v1, env) in reb.items():
                ap = v1[-1]
                if isinstance(ap, tuple): ap = ap[1][-1]
                starts.add(int(lin_at(ap, env, 1000)) % 720)
            if okLB and starts:
                orb = set(starts); fr = list(starts)
                while fr:
                    x = fr.pop(); y = (Da * x + Db) % 720
                    if y not in orb: orb.add(y); fr.append(y)
                lb_halt = []
                for r_ in sorted(orb):
                    if r_ < NCL: h = r_ in hset
                    else:
                        rr, ks = kstep(['H%d' % r_], True, 400000, 60); h = rr == 'HALT'
                    if h: lb_halt.append(r_)
                out('LAST-BORROW route: start classes %s, D: A->%d*A+%d, orbit size %d, halting classes in orbit %s'
                    % (sorted(starts), Da, Db, len(orb), lb_halt[:8]))
                R['last_borrow'] = {'starts': sorted(starts), 'orbit': len(orb), 'halting': lb_halt[:8]}
                if not lb_halt: verdict = 'CONFIRMED(last-borrow: exhaustion classes = D-orbit of %s mod 720, none halts)' % sorted(starts)
        except Exception as ex:
            out('LAST-BORROW route error %r' % ex)
    if verdict is None:
        verdict = 'OPEN(' + ('rules not measured for k=%s' % missing if missing else 'halting exhaustion classes not excluded' if hc else 'exhaustion leaves template/undecided' if und else 'probe mismatches') + ')'
    if bad or miss: verdict += '+DISAGREE(probe_bad=%d,lock_miss=%d)' % (bad, miss)
    R['invariants'] = invs; R['verdict'] = verdict
    out('VERDICT ' + verdict)
    return R

if __name__ == '__main__':
    m0, Q, SIDE = sys.argv[1], sys.argv[2], sys.argv[3]
    TF = [] if sys.argv[4] == '-' else [int(x) for x in sys.argv[4].split(',')]
    Z = int(sys.argv[5]); LSTEPS = int(sys.argv[6]) if len(sys.argv) > 6 else 10**9
    R = audit(m0, Q, SIDE, TF, Z, LSTEPS, int(os.environ.get('NCL', '120')), bool(os.environ.get('LIGHT')), coding=os.environ.get('CODING', 'V'))
    print('JSON ' + json.dumps(R, default=str))
