from xg import *
import itertools, sys
P=sys.argv[1]=='1'
# a-token 0 cases with various t
for toks in [[4,0],[5,0],[6,0],[7,0],[3,0],[2,0],[1,0],[0,0],[8,1,0],[8,2,0],[8,3,0],[8,0,0],[8,4,0],[1,8,0],[0,8,0],[2,8,0],[3,8,0],[9,0],[10,0],[10,1,1,1,0]]:
    for r in (0,3):
        res=litx(toks,r,P,N=3000000)
        print(toks,r,'->',res[0][1:] if res and not isinstance(res[0],str) else res)
