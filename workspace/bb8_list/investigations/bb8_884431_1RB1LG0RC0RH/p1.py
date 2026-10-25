from common import *
print(MIR)
# literal run from blank on mirror: print K configs
s = Sim(MIR)
last=0; n=0
while s.steps < 3000000 and n<60:
    r = run_from(s, 3000000 - s.steps)
    if r[0]!='K':
        print(r[:3]); break
    print('step',r[1],show(r[2]),'[+%d]'%(r[1]-last)); last=r[1]; n+=1
