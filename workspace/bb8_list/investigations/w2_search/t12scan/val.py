"""val.py FILE [--tests std,real,big,fit,order]: Tier-1 validation battery for t12scan hits (one machine per line).
  std  : far_k + [0 1^n|1|19] for (k,n) in (29,323) (71,323) (29,365) (71,365) (29,2843) (113,2843) (29,1415)
         (k1 and depth both 29 mod 42 = the real class, h14verify addendum)
  real : real start b0 = 6, std (wrong class mod 7: info only)
  big  : k = 71, 155 at n = 323, big policy, counters > 1000 trimmed to their class mod 42 (as t1val)
  fit  : big policy bigk = 1, 2, 3 (R = 2539, 5059, 7579) at k = 29, n = 323, untrimmed, to the first RSIG: c, |P|, z
  order: size-order test (as inplace/order.py): bigk = 1 before stage SW (= first RSIG stage + 2), bigk = 20 after
Prints outcome + RSIG list (stage:c:minmw) per test.  Undefined slots of the machine are listed (free slots)."""
import idle  # noqa: F401  (Idle priority, correct HANDLE types)
import sys, threading, argparse
import ilib
from ilib import stage, rsig, far_of, word_of, SUF, real_start
ap = argparse.ArgumentParser(); ap.add_argument('file'); ap.add_argument('--tests', default='std,real,big,fit,order')
ap.add_argument('--S', type=int, default=200); ap.add_argument('--maxs', type=float, default=3e9)
a = ap.parse_args()
TR = [0]
def trim(new, ct):
    out = list(new); i = 0
    while i + 2 < len(out) - 2:
        if out[i] == 2 and out[i + 1] == 5:
            j = i + 2
            while j < len(out) - 2 and out[j] == 1: j += 1
            m = j - i - 2
            if m > 1000:
                m2 = m % 42; out = out[:i + 2] + [1] * m2 + out[j:]; j = i + 2 + m2
            i = j
        else: i += 1
    return out
ilib.trim_counter = trim
def run(M, k, n, pol, real=False, S=200, bigk=1, sw=None, B=20, ctrim=None, stop_rs=None):
    if real: word, head, state = real_start(6)
    else: word, head, state = far_of(k) + word_of([0] + [1] * n + [1, 19]) + SUF, None, 'G'
    rs = []; A = 0; mw = 1 << 60
    ct = (1 if pol == 'big' else 0) if ctrim is None else ctrim
    for st in range(S):
        bk = B if (sw is not None and st >= sw) else bigk
        kind, d = stage(M, word, int(a.maxs), pol, bigk=bk, ctrim=ct, head=head, state=state); head, state = None, 'G'
        if d.get('MW') is not None and d['MW'] < 10**17: mw = min(mw, A + d['MW'])
        if kind != 'K': return f'{kind}{d.get("slot","")}@{st}', rs
        r = rsig(d['toks'])
        if r and st > 0 and r[1] >= 6 and (not rs or st - rs[-1][0] > 3):
            rs.append((st, r[1], len(r[0]), r[2], mw))
            if stop_rs and len(rs) >= stop_rs: return 'RS', rs
        A += d['shift']; word = d['newword']
    return 'MAX', rs
def fmt(rs): return ' '.join(f'{s}:c{c}:P{p}:mw{mw}' for s, c, p, z, mw in rs)
def go():
    tests = a.tests.split(',')
    for M in [l.split()[0] for l in open(a.file) if l.strip() and not l.startswith('#')]:
        free = [q + s for i, q in enumerate('ABCDEFGHIJKLMN') for s in '01' if i < len(M.split('_')) and M.split('_')[i][3 * int(s):3 * int(s) + 3] == '---']
        print(M, 'undefined:', free, flush=True)
        if 'std' in tests:
            for k, n in ((29, 323), (71, 323), (29, 365), (71, 365), (29, 2843), (113, 2843), (29, 1415)):
                o, rs = run(M, k, n, 'std'); print(f'   std k={k} n={n}: {o} RS={fmt(rs)}', flush=True)
        if 'real' in tests:
            o, rs = run(M, 0, 0, 'std', real=True); print(f'   std REAL b0=6 (wrong class mod 7, info only): {o} RS={fmt(rs)}', flush=True)
        if 'big' in tests:
            for k in (71, 155):
                o, rs = run(M, k, 323, 'big'); print(f'   big k={k} n=323: {o} RS={fmt(rs)}', flush=True)
        if 'fit' in tests:
            for bk in (1, 2, 3):
                o, rs = run(M, 29, 323, 'big', bigk=bk, ctrim=0, stop_rs=1, S=60)
                print(f'   fit bigk={bk} (R={19 + 2520 * bk}): {o} ' + (f'c={rs[0][1]} P={rs[0][2]} z={rs[0][3]} mw={rs[0][4]}' if rs else ''), flush=True)
        if 'order' in tests:
            o, rs = run(M, 29, 323, 'std', stop_rs=1)
            sw = (rs[0][0] + 2) if rs else 0
            o, rs = run(M, 29, 323, "big", sw=sw, B=20)
            print(f'   order sw={sw} B=20: {o} RS={fmt(rs)}', flush=True)
threading.stack_size(250 * 1024 * 1024); sys.setrecursionlimit(300000)
t = threading.Thread(target=go); t.start(); t.join()
