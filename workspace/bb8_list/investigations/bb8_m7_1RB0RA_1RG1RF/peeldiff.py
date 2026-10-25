import sys
sys.path.insert(0,'.')
import gen_p0 as g
import planner8 as pl
name=sys.argv[1]; maxpeel=int(sys.argv[2])
st,tg=g.PH[name]
cfgs=[]
orig_try=pl.try_peel
def tp(cfg):
    r=orig_try(cfg)
    if r is not None:
        cfgs.append(cfg)
        if len(cfgs)>=maxpeel: raise SystemExit
    return r
pl.try_peel=tp
try:
    pl.drive(name,st,None,maxev=400,verbose=False)
except SystemExit: pass
def tw(side):
    out=''
    for t in side:
        if isinstance(t,int): out+=str(t)
        elif t==pl.BLANK: out+='|'
        elif t[0]=='run': out+='[%s]^%s'%(''.join(map(str,t[1])),pl.cnt_str(t[2]))
        else: out+='<%s>'%t[1]
    return out
for c in cfgs:
    print(c[0],c[3],'L:',tw(c[1]),' R:',tw(c[2]))
def cells(side):
    out=''
    for t in side:
        if isinstance(t,int): out+=str(t)
        else: break
    return out
cs=[cells(c[1][1:]) for c in cfgs]
for i in range(len(cs)-1):
    a,b=cs[i],cs[i+1]
    print(len(a),len(b), b.endswith(a), b[:len(b)-len(a)] if b.endswith(a) else None)
print(cs[0])
