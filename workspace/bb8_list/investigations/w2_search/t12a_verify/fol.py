"""fol.py M --k K --n N --R R [--policy std] [--stages S] [--real]: verbose follow using the inplace ilib follower
(used only as a map; every claim is re-checked literally elsewhere)."""
import sys, os, threading, argparse
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/w2_search/inplace')
import ilib
from ilib import stage, rsig, far_of, word_of, SUF, rle, real_start
ap = argparse.ArgumentParser(); ap.add_argument('M'); ap.add_argument('--k', type=int, default=17); ap.add_argument('--n', type=int, default=329)
ap.add_argument('--R', type=int, default=19); ap.add_argument('--policy', default='std'); ap.add_argument('--stages', type=int, default=80)
ap.add_argument('--real', action='store_true'); ap.add_argument('--maxs', type=float, default=3e9); ap.add_argument('--start', default=None)
ap.add_argument('--far', default=None); ap.add_argument('--showfar', action='store_true'); ap.add_argument('--full', action='store_true')
a = ap.parse_args()
def go():
    if a.real: word, head, state = real_start(6)
    else:
        far = a.far if a.far is not None else far_of(a.k)
        toks = ilib.expand(a.start) if a.start else [0] + [1] * a.n + [1, a.R]
        word, head, state = far + word_of(toks) + SUF, None, 'G'
    for st in range(a.stages):
        kind, d = stage(a.M, word, int(a.maxs), a.policy, head=head, state=state); head, state = None, 'G'
        if kind != 'K':
            print(st, kind, d.get('slot', ''), d.get('steps', ''), 'U=%x' % d['U'], flush=True); return
        r = rsig(d['toks'])
        print(st, rle(d['toks'][:-2])[:(100000 if a.full else 200)], '| a=%d r=%d' % (d['toks'][-2], d['toks'][-1]), 'far=%d' % len(d['far']), 'ev=%s' % d.get('ev'),
              'U=%x' % d['U'], ('RSIG c=%d z=%d' % (r[1], r[2])) if r else '', flush=True)
        if a.showfar: print('   FAR', d['far'], '/ NEW', rle(d['new']))
        word = d['newword']
    print('MAX')
threading.stack_size(250 * 1024 * 1024); sys.setrecursionlimit(300000)
t = threading.Thread(target=go); t.start(); t.join()
