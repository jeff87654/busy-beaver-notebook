"""audit_r.py: independent audit of the F1-type machines r/s/h/u-like (v-coding [digits.., A, b=2], K = (q,R), z=1).
usage: python audit_r.py MACHINE Q SIDE [literal_steps]
Rules expected (derived on r by symbolic probes):
  D_k: [.., y+1, 0^k, A, 2] -> [.., y, A+3, 2] (k=0) | [.., y, A+3-2k, 2^(k-1), 2, 2] (k>=1)
  E:   [A, 2] -> A odd HALT | A even -> [4, 2^(A/2-1), 2, 2]
The script does NOT assume them: it measures and prints the symbolic outcomes, and compares."""
import sys, idle_guard
from fam import *

m0, Q, SIDE = sys.argv[1], sys.argv[2], sys.argv[3]
LSTEPS = int(sys.argv[4]) if len(sys.argv) > 4 else 10**9
m = mirror(m0) if SIDE == 'L' else m0
B = int(sys.argv[5]) if len(sys.argv) > 5 else 2   # fixed b-run
isK = lambda v, z: z == 1 and len(v) >= 1 and v[-1] == B
def phi(v): return sum(v) % 2
def strip(v):
    while v and v[0] == 0: v = v[1:]
    return v
def rule(v):
    """my rule engine: concrete v (list of int) -> next K v, or 'HALT'/'E' """
    if len(v) < 2: return None
    d, A = v[:-2], v[-2]
    k = 0
    while k < len(d) and d[len(d) - 1 - k] == 0: k += 1
    if k == len(d):   # exhaustion
        return 'E'
    y = d[len(d) - 1 - k]
    pre = d[:len(d) - 1 - k]
    if k == 0: return strip(pre + [y - 1, A + 3, B])
    return strip(pre + [y - 1, A + 3 - 2 * k] + [2] * (k - 1) + [2, B])

print('# machine', m0, 'oriented', m, 'K', Q)
# 1. symbolic rule probes
bad = 0; nprobe = 0
for k in list(range(0, 13)) + [20, 30]:
    for y in [1, 2, 'H3']:
        for left in [[], [3], ['H5']]:
            for Ar in ['H0', 'H1']:
                v0 = left + [y] + [0] * k + [Ar, B]
                r, ks, out = ksteps(m, Q, v0, 1, isK, n=1, prove=False, budget=200000, tlimit=30)
                nprobe += 1
                if r != 'K':
                    print('PROBE', v0, '->', r); bad += 1; continue
                v1, z1, sd = ks[0]; env = symenv(sd)
                # expected
                X = {e: Lin({k2: 1}) for k2, e in []}
                # build expected symbolically
                sy = {}; names = iter(sorted(env, key=lambda s: int(s[1:])))
                exp_in = []
                for e in v0:
                    if isinstance(e, str): exp_in.append(Lin({next(names): 1}))
                    else: exp_in.append(Lin.c(e))
                d, A = exp_in[:-2], exp_in[-2]
                pre = d[:len(d) - 1 - k]; yy = d[len(d) - 1 - k]
                if k == 0: ex = pre + [yy - 1, A + 3, Lin.c(B)]
                else: ex = pre + [yy - 1, A + 3 - 2 * k] + [Lin.c(2)] * (k - 1) + [Lin.c(2), Lin.c(B)]
                while ex and ex[0] == 0: ex = ex[1:]
                got = expand(v1)
                ok = len(got) == len(ex) and all((g - e) == 0 for g, e in zip(got, ex))
                if not ok:
                    bad += 1; print('MISMATCH', v0, 'got', vshow(v1), 'exp', vshow(ex))
print('symbolic rule probes', nprobe, 'mismatches', bad)
# 2. exhaustion classes
hc = []; rb = {}
for r_ in range(48):
    r, ks, out = ksteps(m, Q, ['H%d' % r_, B], 1, isK, n=1, prove=True, budget=400000, tlimit=60)
    if r == 'HALT': hc.append(r_)
    elif r == 'K': rb[r_] = vshow(ks[0][0])
    else: rb[r_] = r
print('exhaustion [X,%d], X = r mod 720 (r<48): HALT classes' % B, hc)
print('  rebuild forms:', sorted(set(rb.values()))[:6])
# 3. literal lockstep and invariant
tr, tail = lit_k(m, Q, LSTEPS)
K = [(s, v) for s, v, z in tr if isK(v, z)]
print('literal K-configs', len(K), 'in', LSTEPS, 'steps;', tail[:60])
print('first K', K[0], ' phi', phi(K[0][1]))
miss = 0; phis = collections.Counter(); nE = 0; ex = []
for (s0, v0), (s1, v1) in zip(K, K[1:]):
    phis[phi(v0)] += 1
    p = rule(v0)
    if p is None: continue
    if p == 'E':
        nE += 1; ex.append((s0, v0[-2], len(v1)))
        continue
    if p != v1:
        miss += 1
        if miss <= 5: print('LOCK MISS at', s0, v0[-8:], '->', v1[-8:], 'pred', p[-8:])
print('lockstep pairs', len(K) - 1, 'misses', miss, 'exhaustions', nE, ex[:5], 'phi counts', dict(phis))
# 3b. borrow margins in the literal run: min over borrows of (A - 2k) by k
mg = {}
for (s0, v0), (s1, v1) in zip(K, K[1:]):
    if len(v0) < 3: continue
    d, A = v0[:-2], v0[-2]; k = 0
    while k < len(d) and d[len(d) - 1 - k] == 0: k += 1
    if 0 < k < len(d): mg[k] = min(mg.get(k, 10**18), A - 2 * k)
print('borrow margins min(A-2k) by k:', dict(sorted(mg.items())))
# 4. constructed literal exhaustions (both phi parities) from small lists
for v in [[1, 0, 0, a, B] for a in range(2, 8)] + [[1, 1, a, B] for a in range(2, 6)] + [[2, 0, a, B] for a in (3, 4)]:
    cells = '0'.join('1' * x for x in v) + '0' + Q + '0'
    tr2, tail2 = lit_k(m, Q, 2 * 10**8, tape=cells)
    K2 = [(s, vv) for s, vv, z in tr2 if isK(vv, z)]
    exh = [(s, vv[0]) for s, vv in K2 if len(vv) == 2][:1]
    big = [(len(vv), phi(vv)) for s, vv in K2 if len(vv) > 6][:1]
    print('constructed', v, 'phi', phi(v), 'exhaustion X', exh, '-> after', big, tail2[:30])
