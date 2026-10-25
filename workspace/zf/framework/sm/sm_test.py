"""Tests for B1.   python -I sm_test.py [K]   (K = exhaustive enumeration bits, default 14)

T0  templates == zf2.py postfix lists (all axioms except B6a, which is the spec's distinctor form)
T1  DAG on the SM == reference decoder (sm_ref) on random candidates with the persistent stack;
    DAG with breakout == DAG without breakout op-trace by op-trace
T2  exhaustive enumeration of all candidates n < 2^K: never halts, full well-formedness check
    after every op, stack equal to the reference after every candidate
T3  planted proofs with the debug check target (SM(check_target=...)):
    a) target = a single axiom instance: first halting candidate of the full persistent
       enumeration == the one predicted by the reference, and it is the candidate encoding it
    b) DET MATCH derivation (B7, B3, DET): halts exactly on its encoding, not on any truncation;
       no candidate < 2^K halts with that target
    c) DET MISMATCH, DET INVALID (no-op), DET underflow (no-op), GEN
"""
import sys, os, random, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sm_prog as P
import sm_ref as R
from sm_abstract import (SM, SMError, candidate_bits, run_enumeration, BOOT_THEOREM, V0, E, EQ, IM,
                         NOT, ALL, parse_tokens, tokstr, is_wff)

K = int(sys.argv[1]) if len(sys.argv) > 1 else 14
P.apply_config()
B, NCELLS = P.build()
DAG, ROOT = B.dag()
CODE, GEN = B.code, B.gen_style
print('cells', NCELLS, 'code', CODE)


def t0():
    sys.path.insert(1, P.EXT)
    import zf2

    class D:
        inc = 'inc'

    class Mock:
        def __getattr__(self, n):
            if n.startswith(('param', 'scratch', 'topwff', 'wffstack', 'axiomcode')):
                return D()
            if n in ('weq', 'wel', 'wim', 'wn', 'wal', 'wex', 'wa', 'select'):
                return lambda: n
            if n.startswith('v_'):
                return lambda: 'v' + n[2:]
            if n.startswith('par'):
                return lambda: n
            return lambda *a: ('X',)
    ax = zf2.ZF2.axioms(Mock())
    names = ['DET', 'GEN', 'B1', 'B2', 'B3', 'B4', 'B6b', 'B8b', 'B6a', 'B6b', 'B6c', 'B7', 'B8a', 'B8b',
             'B8c', 'EXT', 'REP', 'POW', 'UNI', 'INF']
    varp = {'x': (V0 + 5,), 'y': (V0 + 6,), 'z': (V0 + 7,)}
    wffp = {'p1': (E, V0 + 10, V0 + 10), 'p2': (E, V0 + 11, V0 + 11), 'p3': (E, V0 + 12, V0 + 12)}
    nchk = 0
    for nm, lst in zip(names, ax):
        if nm in ('DET', 'GEN', 'B6a'):
            continue
        base = P.AXIOMS[P.AXNAMES.index(nm)][1].split()     # zf2 par_i = i-th param of the spec order
        st = []
        for x in lst:
            if not isinstance(x, str) or x == 'select':
                continue
            if x.startswith('par'):
                p = base[int(x[3:]) - 1]
                st.append(varp[p] if p in varp else wffp[p])
            elif x[0] == 'v':
                st.append((V0 + int(x[1:]),))
            elif x in ('wel', 'weq'):
                b_ = st.pop(); a_ = st.pop(); st.append(((E if x == 'wel' else EQ),) + a_ + b_)
            elif x == 'wim':
                b_ = st.pop(); a_ = st.pop(); st.append((IM,) + a_ + b_)
            elif x == 'wn':
                st.append((NOT,) + st.pop())
            elif x == 'wal':
                b_ = st.pop(); a_ = st.pop(); st.append((ALL,) + a_ + b_)
            elif x == 'wex':
                b_ = st.pop(); a_ = st.pop(); st.append((NOT, ALL) + a_ + (NOT,) + b_)
            elif x == 'wa':
                b_ = st.pop(); a_ = st.pop(); st.append((NOT, IM) + a_ + (NOT,) + b_)
            else:
                raise ValueError(x)
        assert len(st) == 1, (nm, st)
        params = {p: (varp[p] if p in varp else wffp[p]) for p in base}
        mine = P.instantiate(nm, params)
        assert mine == st[0], (nm, tokstr(mine), tokstr(st[0]))
        assert is_wff(mine)
        nchk += 1
    b6a = P.instantiate('B6a', {'x': (V0 + 5,), 'y': (V0 + 6,), 'z': (V0 + 7,)})
    print('T0 ok: %d templates equal zf2.py; B6a = %s' % (nchk, tokstr(b6a)))


def t1(n=1500, seed=1):
    b0, _ = P.build(do_breakout=False)
    d0, r0 = b0.dag()
    rng = random.Random(seed)
    s1 = SM(DAG, ROOT, check='full'); s0 = SM(d0, r0, check='full')
    s1.trace = []; s0.trace = []
    A = [BOOT_THEOREM]
    nsteps = 0
    for it in range(n):
        bits = [rng.randrange(2) for _ in range(rng.randrange(0, 160))]
        o1 = s1.run_candidate(bits); o0 = s0.run_candidate(bits)
        o2, k = R.run(A, bits, CODE, )
        nsteps += k
        assert o1 == o0 == o2 == 'END'
        assert s1.trace == s0.trace
        assert sum(1 for t in s1.trace if t[0] == 'CHECK') == k      # one CHECK per complete step
        s1.trace.clear(); s0.trace.clear()
        assert s1.A == A == s0.A
        assert s1.B == [] and s1.c == 0 and s1.P == []
    print('T1 ok: %d random candidates, %d steps, |A|=%d, DAG==reference, breakout==hashcons' % (n, nsteps, len(A)))


def t2(k=K):
    t = time.time()
    sm = SM(DAG, ROOT, check='full')
    A = [BOOT_THEOREM]
    from collections import Counter
    cnt = Counter()
    for n in range(1 << k):
        bits = candidate_bits(n)
        r = sm.run_candidate(bits)
        steps, _ = R.decode(bits, CODE)
        cnt.update(s[0] for s in steps)
        r2, _ = R.run(A, bits, CODE)
        assert r == r2 == 'END', (n, r, r2)
        # top entries every candidate (entries below the top are immutable); full compare at the end
        assert len(sm.A) == len(A) and sm.A[-8:] == A[-8:], n
    assert sm.A == A
    print('T2 ok: all %d candidates < 2^%d: no halt, no SMError, stack == reference (|A|=%d, %d ops, %.0fs)'
          % (1 << k, k, len(sm.A), sm.nops, time.time() - t))
    print('   steps per axiom:', dict(sorted(cnt.items(), key=lambda kv: P.AXNAMES.index(kv[0]))))
    missing = [a for a in P.AXNAMES if a not in cnt]
    if missing:
        print('   (axioms not reached below 2^%d: %s; covered by T1/T3)' % (k, missing))


def first_halt_reference(target, limit):
    A = [BOOT_THEOREM]
    for n in range(limit):
        r, _ = R.run(A, candidate_bits(n), CODE, target)
        if r == 'HALT':
            return n
    return None


def pad(bits):
    """smallest candidate whose read-order bits start with `bits` (candidates end with bit 1)"""
    return list(bits) if bits and bits[-1] == 1 else list(bits) + [1]


def st(name, **kw):
    """step with params given by name, put into the configured reading order"""
    return (name, tuple(kw[p] for p in P.AXDICT[name][1].split()))


def t3():
    v = lambda i: (V0 + i,)
    # a) single axiom instance target
    for nm, ps in [st('B8a', x=v(0), y=v(0), z=v(0)), st('B7', x=v(1), y=v(0)), st('B2', p1=(E, V0, V0))]:
        target = P.instantiate(nm, dict(zip(P.AXDICT[nm][1].split(), ps)))
        enc = R.encode([(nm, ps)], CODE, GEN)
        cand = pad(enc)
        ncand = sum(b << i for i, b in enumerate(cand))
        nref = first_halt_reference(target, 1 << 20)
        nsm, sm = run_enumeration(DAG, ROOT, 21, check='full', check_target=target, stop_n=ncand)
        print('T3a %s%s: encoding %s (candidate n=%d); first halt: SM n=%s, reference n=%s'
              % (nm, tuple(tokstr(p) for p in ps), ''.join(map(str, enc)), ncand, nsm, nref))
        assert nsm == nref
        assert nsm <= ncand
        if nsm == ncand:
            print('     -> halts exactly on the candidate encoding the derivation, on no smaller one')
        else:
            print('     -> an earlier candidate %s already derives it (prefix-sharing / persistent stack)'
                  % ''.join(map(str, candidate_bits(nsm))))
    # b) DET MATCH derivation
    Y = P.instantiate('B7', {'x': v(0), 'y': v(1)})              # E v0 = v0 v1
    q = (E, V0, V0)
    X = P.instantiate('B3', {'p1': Y, 'p2': q})                  # -> Y -> ~ Y e v0 v0
    ps_ = X[1 + len(Y):]
    steps = [st('B7', x=v(0), y=v(1)), st('B3', p1=Y, p2=q), ('DET', ())]
    enc = R.encode(steps, CODE, GEN)
    cand = pad(enc)
    sm = SM(DAG, ROOT, check='full', check_target=ps_)
    sm.trace = []
    r = sm.run_candidate(cand)
    assert r == 'HALT', r
    assert sm.A == [BOOT_THEOREM, ps_], [tokstr(t) for t in sm.A]
    assert sm.rpos == len(enc) and sm.trace[-1][0] == 'CHECK' and sm.trace[-2][0] == 'DET'
    assert sm.last_det == 'match'
    for L in range(len(enc)):
        s2 = SM(DAG, ROOT, check='full', check_target=ps_)
        assert s2.run_candidate(cand[:L]) == 'END'
    nh, _ = run_enumeration(DAG, ROOT, K, check='incremental', check_target=ps_)
    assert nh is None
    print('T3b DET MATCH: B7(v0,v1); B3(p1=Y, p2=e v0 v0); DET  -> ps = %s' % tokstr(ps_))
    print('     encoding %d bits %s; halts on it right after the DET step (all %d bits read),'
          % (len(enc), ''.join(map(str, enc)), len(enc)))
    print('     no truncation halts (fresh stack), no candidate < 2^%d halts with this target' % K)
    # c) DET MISMATCH / INVALID / underflow / GEN
    X2 = P.instantiate('B8a', {'x': v(0), 'y': v(0), 'z': v(0)})
    sm = SM(DAG, ROOT, check='full')
    sm.run_candidate(pad(R.encode([('DET', ())], CODE, GEN)))
    assert sm.last_det == 'underflow' and sm.A == [BOOT_THEOREM]
    sm.run_candidate(pad(R.encode([st('B7', x=v(0), y=v(1)), st('B8a', x=v(0), y=v(0), z=v(0)), ('DET', ())], CODE, GEN)))
    assert sm.last_det == 'mismatch' and sm.A[-1] == Y and len(sm.A) == 2, [tokstr(t) for t in sm.A]
    sm.run_candidate(pad(R.encode([st('B7', x=v(2), y=v(2)), ('DET', ())], CODE, GEN)))
    assert sm.last_det == 'invalid' and sm.A[-1] == P.instantiate('B7', {'x': v(2), 'y': v(2)}) and len(sm.A) == 3
    sm.run_candidate(pad(R.encode([('GEN', (v(3),))], CODE, GEN)))
    assert sm.A[-1] == (ALL, V0 + 3) + sm.A[-2]
    print('T3c ok: DET underflow no-op, DET MISMATCH (X erased, Y kept), DET INVALID no-op, GEN')


if __name__ == '__main__':
    t0()
    t1()
    t3()
    t2()
