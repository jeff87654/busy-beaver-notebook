import sys
from ev6 import *
n=C(3,n=1)
def R_of(spec): return toks(spec)
L=toks([('01',n)],left=True)
spec=eval(sys.argv[1])
run_events(('A',L,R_of(spec),'>'),int(sys.argv[2]),verbose=len(sys.argv)>3)
