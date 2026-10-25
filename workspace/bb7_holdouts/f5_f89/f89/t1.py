from msim import *
a=V('a',1)*2+1; b=V('b',1)*2+1; c=V('c',1)*2+1; k=V('k',2)
for cfg in ([a,b+2,c],[a,('Z',k),b+2,c],[a,('Z',k)],[a,1,('Z',k)],[a]):
    try:
        r,s=next_K(cfg); print(show(cfg),'->',show(r), s.steps, s.macro)
    except Fail as e: print(show(cfg),'FAIL',e)
