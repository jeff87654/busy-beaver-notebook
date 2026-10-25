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

def audit(m0, Q, SIDE, TF, Z, LSTEPS=10**9, NCL=120, light=False, out=print):
    R = {'machine': m0}
    m = mirror(m0) if SIDE == 'L' else m0
    nT = len(TF)
    def isK(v, z):
        if z != Z or len(v) < 1 + nT: return False
        tl = v[len(v) - nT:]
        for e, t in zip(tl, TF):
            if isinstance(e, tuple): return False
            if isinstance(e, Lin):
                if not e.isconst() or e.const() != t: return False
            elif e != t: return False
        return True
    def split(v): return v[:len(v) - 1 - nT], v[len(v) - 1 - nT]
    out('# machine %s side %s oriented %s K %s TF %s z %d' % (m0, SIDE, m, Q, TF, Z))
    def probe(left, y, k, Ar):
        v0 = left + [y] + [0] * k + [Ar] + TF
        r, ks, raw = ksteps(m, Q, v0, Z, isK, n=1, prove=False, budget=300000, tlimit=30)
        if r != 'K': return v0, r, None, None
        v1, z1, sd = ks[0]; env = symenv(sd)
        names = sorted(env, key=lambda s: int(s[1:])); it = iter(names); sub = []
        for e in v0: sub.append(Lin({next(it): 1}) if isinstance(e, str) else Lin.c(e))
        return v0, 'K', sub, expand(v1)
    KS = list(range(0, 7)) + [12, 20] if light else list(range(0, 13)) + [20, 30]
    rules = {}
    for k in KS:
        v0, r, sub, got = probe([], 'H3', k, 'H0')
        if r != 'K': out('RULE k=%d: %s' % (k, r)); rules[k] = r; continue
        y = sub[0]; rest = got[:len(got) - nT]
        if not (rest and (rest[0] - (y - 1)) == 0): out('RULE k=%d unexpected head %s' % (k, vshow(got))); rules[k] = 'odd'; continue
        rules[k] = rest[1:]
        out('RULE k=%2d: [y+1,0^%d,A] -> [y, %s]' % (k, k, vshow(rest[1:])))
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
            for left in ([[], ['H5']] if light else [[], [3], ['H5'], [1, 0]]):
                if left == [1, 0] and k > 6: continue
                for Ar in (['H0', 'H1'] if light else ['H0', 'H1', 'H2']):
                    n += 1
                    v0, r, sub, got = probe(left, y, k, Ar)
                    ref = rules.get(k)
                    if r != 'K' or not isinstance(ref, list):
                        if r != 'K' and isinstance(ref, list): out('PROBE %s %s' % (v0, r)); bad += 1
                        continue
                    d, A = sub[:len(sub) - 1 - nT], sub[len(sub) - 1 - nT]
                    yy = d[len(left)]; pre = d[:len(left)]
                    bA = baseA(ref)
                    pred = pre + [yy - 1] + [subst(e, bA, A) for e in ref] + [Lin.c(t) for t in TF]
                    while pred and pred[0] == 0: pred = pred[1:]
                    ok = len(pred) == len(got) and all((a - b) == 0 for a, b in zip(pred, got))
                    if not ok:
                        bad += 1
                        if bad <= 8: out('MISMATCH %s got %s pred %s' % (v0, vshow(got), vshow(pred)))
    out('symbolic probes %d mismatches %d' % (n, bad))
    R['probes'] = n; R['probe_bad'] = bad
    # exhaustion classes
    hc = []; rbf = collections.Counter(); und = []; reb = {}
    for r_ in range(NCL):
        r, ks, raw = ksteps(m, Q, ['H%d' % r_] + TF, Z, isK, n=1, prove=True, budget=400000, tlimit=60)
        if r == 'HALT': hc.append(r_)
        elif r == 'K': rbf[vshow(ks[0][0])] += 1; reb[r_] = (ks[0][0], symenv(ks[0][2]))
        else: und.append((r_, r))
    out('EXHAUSTION [X]+TF, X = r mod 720, r < %d: HALT classes %s (%d) not-K %s' % (NCL, hc[:40], len(hc), und[:5]))
    for f, c in rbf.most_common(4): out('   rebuild %d x %s' % (c, f))
    R['halt_classes'] = hc; R['exh_notK'] = und; R['rebuild'] = [f for f, c in rbf.most_common(3)]
    # literal lockstep
    def nxt(v):
        if len(v) < 1 + nT: return None
        d, A = split(v)
        k = 0
        while k < len(d) and d[len(d) - 1 - k] == 0: k += 1
        if k == len(d): return 'E'
        ref = rules.get(k)
        if not isinstance(ref, list):
            # extrapolate from the measured family when k not probed: refill/tail pattern of k-1 and k-2
            return None
        bA = baseA(ref)
        y = d[len(d) - 1 - k]; pre = d[:len(d) - 1 - k]
        o = pre + [y - 1] + [int(subst(e, bA, Lin.c(A)).const()) for e in ref] + TF
        while o and o[0] == 0: o = o[1:]
        return o
    tr, tail = lit_k(m, Q, LSTEPS)
    K = [(s, v) for s, v, z in tr if isK(v, z)]
    out('literal K-configs %d in %d steps; %s first %s' % (len(K), LSTEPS, tail[:40], K[:2]))
    miss = 0; nE = 0; ex = []; skip = 0; margins = {}
    for (s0, v0), (s1, v1) in zip(K, K[1:]):
        p = nxt(v0)
        if p is None: skip += 1; continue
        if p == 'E': nE += 1; ex.append((s0, split(v0)[1], len(v1))); continue
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
                for (s0, v0), (s1, v1) in zip(K, K[1:]):
                    p = nxt(v0)
                    if p == 'E' or p is None: continue
                    f0, f1 = feats(v0), feats(v1)
                    if (wD * (f1[0] - f0[0]) + wA * (f1[1] - f0[1])) % mm: ok = False; break
                if not ok: continue
                for k, ref in rules.items():
                    if not isinstance(ref, list): continue
                    newd, newA = ref[:-1], ref[-1]
                    bA = baseA(ref); Aval = Lin({bA: 1}) if bA else Lin.c(0)
                    delta = wD * (-1 + sum(newd, Lin.c(0))) + wA * (newA - Aval)
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
            tot = Fr(0); vv = v1[:len(v1) - nT]
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
        if not bad_h and rb_ok and hc: verdict = 'CONFIRMED(invariant %s=%d excludes halting exhaustion classes)' % ((mm, wD, wA), pv)
    if not hc and not und and bad == 0: verdict = verdict or 'CONFIRMED(no halting exhaustion class r<%d; rules halt-free in probes)' % NCL
    if verdict is None:
        verdict = 'OPEN(' + ('halting exhaustion classes not excluded' if hc else 'exhaustion leaves template/undecided' if und else 'probe mismatches') + ')'
    if bad or miss: verdict += '+DISAGREE(probe_bad=%d,lock_miss=%d)' % (bad, miss)
    R['invariants'] = invs; R['verdict'] = verdict
    out('VERDICT ' + verdict)
    return R

if __name__ == '__main__':
    m0, Q, SIDE = sys.argv[1], sys.argv[2], sys.argv[3]
    TF = [] if sys.argv[4] == '-' else [int(x) for x in sys.argv[4].split(',')]
    Z = int(sys.argv[5]); LSTEPS = int(sys.argv[6]) if len(sys.argv) > 6 else 10**9
    R = audit(m0, Q, SIDE, TF, Z, LSTEPS, int(os.environ.get('NCL', '120')), bool(os.environ.get('LIGHT')))
    print('JSON ' + json.dumps(R, default=str))
