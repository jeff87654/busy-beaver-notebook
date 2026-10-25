from common import *
# R4 probes
for bp in (1,3,5,7,9,11,13):
    r = run_next(MIR,(),0,bp,N=10**6); print('R4 bp',bp, show(r[2]) if r[0]=='K' else r[:3], r[1])
# R3 with different y and digits above
for y in (1,2,3):
  for bp in (9,):
    for k in (1,2,3):
        r = run_next(MIR,(3,y)+(0,)*k,0,bp,N=10**6); print('y+1',y,'bp',bp,'k',k, show(r[2]) if r[0]=='K' else r[:3])
# R1/R2
for bp in (1,3,5,7):
    print('R1',show(run_next(MIR,(2,),2,bp)[2]), 'R2', show(run_next(MIR,(3,2),0,bp)[2]))
