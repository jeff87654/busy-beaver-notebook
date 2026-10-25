"""r2sweep.py M --cs .. --zs .. --K1s .. --Ps .. --rs ..: round-2 start word (stage-14 jump output of T12a):
far = (10101)^K1 + TAIL22, digits [3, P, 2, 5] + 1^c + [0,0,0,3] + 1^z, a=1 (last 1), r.  Follow to the outcome.
Reports outcome, stage, the next RSIG (if any), and the D2 count / tokens at the last K-moment before the end."""
import sys, threading, argparse, time
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/w2_search/inplace')
import ilib
from ilib import stage, rsig, word_of, SUF, rle
from sweep_util import rng
TAIL22 = '1011010101010101010100'
ap = argparse.ArgumentParser(); ap.add_argument('M'); ap.add_argument('--cs', default='19'); ap.add_argument('--zs', default='355')
ap.add_argument('--K1s', default='10'); ap.add_argument('--Ps', default='42'); ap.add_argument('--rs', default='19'); ap.add_argument('--pre', default='3')
ap.add_argument('--policy', default='std'); ap.add_argument('--S', type=int, default=600); ap.add_argument('--v', action='store_true')
ap.add_argument('--tail', default=TAIL22); ap.add_argument('--maxs', type=float, default=3e9)
a = ap.parse_args()
def go():
    for K1 in rng(a.K1s):
      for P in rng(a.Ps):
        for c in rng(a.cs):
          for z in rng(a.zs):
            for r in rng(a.rs):
                pre = [int(x) for x in a.pre.split()] if a.pre else []
                word = '10101' * K1 + a.tail + word_of(pre + [P, 2, 5] + [1] * c + [0, 0, 0, 3] + [1] * z + [r]) + SUF
                t = time.time(); last = None; out = 'MAX'; rs = None
                for st in range(a.S):
                    kind, d = stage(a.M, word, int(a.maxs), a.policy)
                    if kind != 'K': out = f'{kind}{d.get("slot","")}@{st}'; break
                    if a.v: print('   ', st, rle(d['toks'][:-2])[:150], 'far', len(d['far']), flush=True)
                    g = rsig(d['toks'])
                    if g and st > 2: rs = (st, list(g[0])[:6], g[1], g[2]); out = 'RSIG'; break
                    last = d; word = d['newword']
                lt = rle(last['toks'][:-2])[:90] if last else ''
                print(f'K1={K1} P={P} c={c} (mod14={c%14} mod42={c%42}) z={z} r={r}: {out} {rs or ""} last=[{lt}] ({time.time()-t:.0f}s)', flush=True)
threading.stack_size(250 * 1024 * 1024); sys.setrecursionlimit(300000)
t = threading.Thread(target=go); t.start(); t.join()
