import sys
from tmlit import Sim, ST
TM='1RB0RH_0LC1LF_1LE0RD_1RC---_0RG0LF_0LB1RA_1RH1RD_0LE1RD'
s=Sim(TM,1<<20)
a=int(sys.argv[1]); b=int(sys.argv[2])
while s.steps<a: s.step()
base=s.pos
out=[]
while s.steps<b:
    out.append((s.steps,s.pos-base,ST[s.state])); s.step()
# print local extremes
for i in range(1,len(out)-1):
    if (out[i][1]-out[i-1][1])*(out[i+1][1]-out[i][1])<0 and True:
        pass
# print sampled position and state every 10 steps
print(' '.join('%d:%d%s'%(x[0]-a,x[1],x[2]) for x in out[::25]))
