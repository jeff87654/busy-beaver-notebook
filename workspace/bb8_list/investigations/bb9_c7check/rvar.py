# rvar.py: same chain but with a DIFFERENT accumulator at every CL (R cycles through a list), to check that the counter
# rounds and exits do not depend on R beyond X = 6R+7.
import idle, sys
from chain import chain
K = int(sys.argv[1]); Rs = [int(x) for x in sys.argv[2].split(',')]
print(f'# K6={K} R cycle {Rs}', flush=True)
chain(f'0,2,z2,1*{K-2};1;{3*Rs[0]+2};6', [], lambda i, r: Rs[(i+1) % len(Rs)], 400, log=lambda s: print(s, flush=True), cnt=False)
