from psim import *
import sys
n=int(sys.argv[1]); 
st={'min':0,'max':0}
def f(q,s,pos,tape):
    r=False
    if pos<st['min'] or pos>st['max']+50:
        pass
    if pos<st['min']: st['min']=pos; r=True
    return r
run(n,f)
