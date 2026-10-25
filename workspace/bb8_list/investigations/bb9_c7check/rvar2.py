# rvar2.py K' : main counter loop from Kt(0,0,1,7,z2,1^K';1;3R5+2;6) with a different accumulator at every CL
import idle, sys
from chain import chain
Kp = int(sys.argv[1]); Rs = [16, 366, 116, 41, 1101, 6]
def stop(r):
    v = r['view']; return not (v.startswith('0*3 ') or v.startswith('0*4 ') or v.startswith('0 2 z2 '))
chain(f'0,0,1,7,z2,1*{Kp};1;{3*11+2};6', [], lambda i, r: Rs[i % len(Rs)], 300, log=lambda s: print(s[:160], flush=True), stop=stop, cnt=False, multi=False)
