"""exp1: J0 completions with existing states (40 machines), followed from the real start b0=6 for 120 stages."""
import sys, threading
from nfol import *
base = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_{}0LC'
sys.setrecursionlimit(30000); threading.stack_size(64 * 1024 * 1024)
def go():
    for w in '01':
        for d in 'LR':
            for q in 'ABCDEFGHIJ':
                M = base.format(w + d + q)
                lines = []
                r, H = follow(M, 6, 'std', 120, 2 * 10**8, log=lines.append)
                ks = [h for h in H if h[1] == 'K']
                last = lines[-1][:160] if lines else ''
                # longest run of 1s left of the cleared list in any K after stage 37
                best = 0
                for h in ks:
                    if h[0] < 37: continue
                    t = h[2][:-2]; run = 0
                    for x in t:
                        run = run + 1 if x == 1 else 0
                        best = max(best, run)
                print(f'{w+d+q} {r} stages={len(ks)} maxrun1_after37={best} | {last}', flush=True)
t = threading.Thread(target=go); t.start(); t.join()
