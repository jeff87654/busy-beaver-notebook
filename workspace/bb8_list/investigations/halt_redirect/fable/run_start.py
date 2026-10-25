import sys, argparse, threading
sys.setrecursionlimit(1000000)
threading.stack_size(256*1024*1024 - 4096)
sys.path.insert(0, '.')
import gh_run
ap = argparse.ArgumentParser(); ap.add_argument('fam'); ap.add_argument('u', type=int); ap.add_argument('--policy', default='std')
ap.add_argument('--bigk', type=int, default=1); ap.add_argument('--stages', type=int, default=20000); ap.add_argument('--maxs', type=int, default=1_000_000_000)
ap.add_argument('--log', required=True)
a = ap.parse_args()
u = a.u
start = [9]*u + [11] + [1]*(2*u+36) + [1, 2] if a.fam == 'R1' else [227] + [9]*u + [8,3,1,0,0,9] + [1]*(2*u+1) + [1, 1]
lf = open(a.log, 'w')
def log(s):
    lf.write(s + '\n'); lf.flush()
def main():
    res = gh_run.follow(0, a.policy, a.stages, a.maxs, a.bigk, log=log, start=start)
    log('RESULT ' + res); print(a.fam, u, a.policy, res)
t = threading.Thread(target=main); t.start(); t.join()
