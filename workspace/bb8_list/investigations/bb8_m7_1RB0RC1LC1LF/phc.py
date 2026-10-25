"""phase definitions for champ12 machines (planner configs) + Coq statement generation"""
import planner8 as pl
from planner8 import mkrun, V, BLANK
TMS={'1':'1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RG0LC_1RG1LD_0LH0RF_---1RE','2':'1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RG0LC_1RG1LD_0RH0RF_---1LE'}
SUF=[1,0,0,1,1,1]
U=(0,1); UR=(1,0)
CTX=[0,1,0,1,1,0,1]

def cnt_coq(c):
    parts=[]
    for k,v in c:
        parts.append(k if v==1 else '%d * %s'%(v,k))
    return '(' + ' + '.join(parts) + ')'

def side2coq(side):
    out=''
    for t in side:
        if isinstance(t,int): out+='%d >> '%t
        elif t==pl.BLANK: out+='const 0'; return out
        elif t[0]=='VAR': out+=t[1]; return out
        else:
            blk=';'.join(map(str,t[1]))
            out+='[%s]^^%s *> '%(blk,cnt_coq(t[2]))
    raise RuntimeError('side without terminator')

def cfg2coq(cfg):
    q,L,R,mode=cfg
    assert mode=='>'
    return '(%s) {{%s}}> (%s)'%(side2coq(L),q,side2coq(R))

def varnames(*cfgs):
    names=set()
    for cfg in cfgs:
        for side in (cfg[1],cfg[2]):
            for t in side:
                if isinstance(t,tuple) and t[0]=='VAR': names.add(t[1])
                if isinstance(t,tuple) and t[0]=='run':
                    for k,v in t[2]: names.add(k)
    return sorted(names)

def stmt(start,target,eqs=(),hyps=()):
    """eqs: list of (name, lin-form) meaning name = sum ; hyps: extra coq hypotheses strings"""
    names=varnames(start,target)
    h=''.join('%s -> '%x for x in hyps)
    for nm,c in eqs: h+='%s = %s -> '%(nm,cnt_coq(c))
    return 'forall %s, %s%s -->+ %s'%(' '.join(names),h,cfg2coq(start),cfg2coq(target))
