"""myfol.py: mini-follower (halt_redirect/mf/ord_run.follow, family C7 = BB(7) champion engine, Q=B, SUF=11001, E=2)
for a 9-state c7m12 machine, started from the real first-exhaustion configuration K(0^11; 0; b0) (literal word).
usage: python myfol.py MACHINE [--b0 6] [--policy std|big|shrink] [--stages 60] [--maxs 1e8] [--log F]"""
import sys, argparse, threading
HR = r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/halt_redirect'
sys.path.insert(0, HR + '/c7'); sys.path.insert(0, HR + '/mf')
import c7fam, mf35g, ord_run
ap = argparse.ArgumentParser()
ap.add_argument('machine'); ap.add_argument('--b0', type=int, default=6); ap.add_argument('--policy', default='std')
ap.add_argument('--stages', type=int, default=60); ap.add_argument('--maxs', type=float, default=1e8)
ap.add_argument('--bigk', type=int, default=1); ap.add_argument('--log', default=None)
ap.add_argument('--start', default=None, help='token list farthest-first incl. a and r (default: K(0^11;0;b0))')
a = ap.parse_args()
m = a.machine
while m.count('_') < 9: m += '_------'
def expand(s):
    v = []
    for t in s.split():
        if '^' in t: x, c = t.split('^'); v += [int(x)] * int(c)
        else: v.append(int(t))
    return v
start = expand(a.start) if a.start else [0, 0] + [1] * 12 + [3 * a.b0 + 2]
lf = open(a.log, 'w') if a.log else None
def log(s):
    print(s, flush=True)
    if lf: lf.write(s + '\n'); lf.flush()
log(f'# {a.machine} b0={a.b0} policy={a.policy} start={a.start or "K(0^11;0;b0)"}')
sys.setrecursionlimit(30000); threading.stack_size(64 * 1024 * 1024)
res = []
t = threading.Thread(target=lambda: res.append(ord_run.follow(a.b0, a.policy, a.stages, int(a.maxs), a.bigk, log=log,
                                                              start=start, FAM='C7', M=m)))
t.start(); t.join()
log(f'RESULT {res[0] if res else "CRASH"}')
