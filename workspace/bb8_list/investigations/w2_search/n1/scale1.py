import sys, threading
from nfol import *
from per import per_m
sys.setrecursionlimit(30000); threading.stack_size(64 * 1024 * 1024)
M = sys.argv[1]; stages = int(sys.argv[2]) if len(sys.argv) > 2 else 40
def go():
    for k in (3,):
        for n in (60, 120, 240):
            for R in (19, 2539):
                lines = []
                r, H = follow(M, policy='std', stages=stages, log=lines.append, start=[0] + [1]*n + [1, R], far='10101'*k + FAR_TAIL)
                pers = [(h[0],) + p for h in H if h[1] == 'K' for p in per_m(h[2])]
                zs = [h[2][:-2] for h in H if h[1]=='K']
                print(f'k={k} n={n} R={R}: {r} stages={len(H)} per(stage,x,m,zeros)={pers[:12]}', flush=True)
t = threading.Thread(target=go); t.start(); t.join()
