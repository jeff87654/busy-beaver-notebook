"""fol.py: verbose follower (ord_run.follow) for any GH-family machine from the real start or a constructed token start.
usage: python fol.py MACHINE [--start "9^3 1^5 1 19"] [--policy std|big|shrink] [--stages 80] [--maxs 2e8] [--b0 6] [--bigk 1] [--log F]"""
import sys, argparse, os
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/halt_redirect/mf')
import ord_run
def expand(s):
    v = []
    for t in s.split():
        if '^' in t:
            x, c = t.split('^'); v += [int(x)] * int(c)
        else:
            v.append(int(t))
    return v
ap = argparse.ArgumentParser()
ap.add_argument('machine'); ap.add_argument('--start', default=None); ap.add_argument('--policy', default='std')
ap.add_argument('--stages', type=int, default=80); ap.add_argument('--maxs', type=float, default=2e8); ap.add_argument('--b0', type=int, default=6)
ap.add_argument('--bigk', type=int, default=1); ap.add_argument('--cap', type=int, default=3); ap.add_argument('--log', default=None); ap.add_argument('--fam', default='GH')
a = ap.parse_args()
m = a.machine
if m.count('_') == 8: m += '_------'
lf = open(a.log, 'w') if a.log else None
def log(s):
    print(s, flush=True)
    if lf: lf.write(s + '\n'); lf.flush()
import threading
sys.setrecursionlimit(30000); threading.stack_size(64 * 1024 * 1024)
res = []
def _go():
    res.append(ord_run.follow(a.b0, a.policy, a.stages, int(a.maxs), a.bigk, cap=a.cap, log=log, start=expand(a.start) if a.start else None, FAM=a.fam, M=m))
t = threading.Thread(target=_go); t.start(); t.join()
r = res[0] if res else 'CRASH'
log(f'RESULT {r}')
