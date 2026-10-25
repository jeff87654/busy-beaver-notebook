# cntgrid.py: post-J6 counter loop and its exit, over K' (list length) and R values.
import idle, sys
from chain import chain
def one(Kp, R5, R, t=6):
    lines = []
    def stop(r):
        v = r['view']
        return not (v.startswith('0*3 ') or v.startswith('0*4 ') or v.startswith('0 2 z2 '))
    h = chain(f'0,0,1,7,z2,1*{Kp};1;{3*R5+2};{t}', [], lambda i, r: R, 200, log=lines.append, stop=stop)
    return lines
for Kp in map(int, sys.argv[1].split(',')):
    for R5, R in [(6, 366), (11, 116)]:
        L = one(Kp, R5, R)
        print(f"K'={Kp} (mod5 {Kp%5}) R5={R5} R={R}: first {L[0][:80]} ... n_cl={len(L)}", flush=True)
        for l in L[-3:]: print('   ', l[:200], flush=True)
