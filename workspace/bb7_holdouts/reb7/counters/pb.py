import idle, sys
from thr import rlg
M,O,Q,u,s,S=sys.argv[1:7]; mo=int(sys.argv[7]) if len(sys.argv)>7 else 3
for line in sys.stdin:
    line=line.strip()
    if not line: continue
    if '|' in line:
        pm,rest=line.split('|'); m=int(pm); inp='P:'+'10'*m+'1 '+rest
    else: inp=line
    print('>>',line)
    for l in rlg(M,O,Q,u,s,S,inp,10**8,mo,0): print('   ',l[:160])
