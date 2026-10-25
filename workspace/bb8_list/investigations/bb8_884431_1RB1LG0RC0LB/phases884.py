"""Phase definitions for 1RB1LG_0RC0LB_1RD0LA_1LE0RH_1RF1RE_0LA0LG_1LC1LA_---0RE (planner configs) and a
converter from planner configs to Coq statements."""
import planner8 as pl
from planner8 import mkrun, V, BLANK
U=(1,1); O=(1,); Z=(0,)
TM='1RB1LG_0RC0LB_1RD0LA_1LE0RH_1RF1RE_0LA0LG_1LC1LA_---0RE'

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

def stmt(start,target,vars_=None):
    # collect variable names
    names=set()
    for cfg in (start,target):
        for side in (cfg[1],cfg[2]):
            for t in side:
                if isinstance(t,tuple) and t[0]=='VAR': names.add(t[1])
                if isinstance(t,tuple) and t[0]=='run':
                    for k,v in t[2]: names.add(k)
    names=sorted(names)
    return 'forall %s, %s -->+ %s'%(' '.join(names),cfg2coq(start),cfg2coq(target))

BL=[BLANK]
def run(blk,var,c=0): return mkrun(blk,{var:1},c)

PH={}
# R1: B> 000 (11)^b 0 11 (11)^a rr -> B> 000 (11)^(b+2) 0 (11)^a rr
PH['R1P']=(('B',BL,[0,0,0]+run(U,'b')+[0,1,1]+run(U,'a')+[V('rr')],'>'),
           ('B',BL,[0,0,0]+run(U,'b',2)+[0]+run(U,'a')+[V('rr')],'>'))
PH['R2P']=(('B',BL,[0,0,0]+run(U,'b')+[0,0,1,1]+run(U,'x')+[V('rr')],'>'),
           ('B',BL,[0,0,0,0]+run(U,'b',2)+[0]+run(U,'x')+[V('rr')],'>'))
PH['R3K1']=(('B',BL,[0,0,0]+run(U,'b')+[0,0,0,1,1]+run(U,'y')+[V('rr')],'>'),
            ('B',BL,[0]*5+run(U,'b',2)+[0]+run(U,'y')+[V('rr')],'>'))
# k = j+2 : TR, LOOP, FINAL
PH['TR']=(('B',BL,[0,0,0]+run(U,'b')+[0,0,0,0]+run(Z,'j')+[1,1]+run(U,'y')+[V('rr')],'>'),
          ('H',[0,1,1,1,BLANK],run(U,'b')+[1,1,1]+run(Z,'j',1)+[1,1]+run(U,'y')+[V('rr')],'>'))
PH['LOOP']=(('H',[0,1,1,1,V('l')],run(U,'b')+[1,1,1,0,0,V('X')],'>'),
            ('H',[0,1,1,1,1,V('l')],run(U,'b')+[1,1,1,0,V('X')],'>'))
PH['FINAL']=(('H',[0]+run(O,'j',3)+[BLANK],run(U,'b')+[1,1,1,0,1,1]+run(U,'y')+[V('rr')],'>'),
             ('B',BL,[0]*6+run(Z,'j')+run(U,'b',2)+[0]+run(U,'y')+[V('rr')],'>'))
# all-zero list (n = u*2+3 zero digits), gap = n+1 zeros then the prefix 1
PH['ZTR']=(('B',BL,[0,0,0]+run(U,'b')+[0,0,0,0]+run(Z,'j')+[1,BLANK],'>'),
           ('H',[0,1,1,1,BLANK],run(U,'b')+[1,1,1]+run(Z,'j',1)+[1,BLANK],'>'))
PH['ZM1']=(('H',[0,1,1,1]+run(U,'u')+[BLANK],run(U,'b')+[1,1,1,0,1,BLANK],'>'),
           ('B',BL,[0,0,0,1]+run(U,'u')+[0]+run(U,'b')+[1,1,1,1,1,1,BLANK],'>'))
PH['ZM2']=(('B',BL,[0,0,0,1]+run(U,'u')+[0,1,1,1]+run(O,'r')+[BLANK],'>'),
           ('F',[1,1,1,1]+run(U,'u')+[0,0,1,1,1,BLANK],run(O,'r')+[BLANK],'>'))
PH['LOOP3']=(('F',[1,1,1,1]+run(U,'u')+[0,0]+run(O,'j')+[1,1,1,BLANK],[1]+run(O,'m')+[BLANK],'>'),
             ('F',[1,1,1,1]+run(U,'u')+[0,0,1]+run(O,'j')+[1,1,1,BLANK],run(O,'m')+[BLANK],'>'))
PH['S2C']=(('F',[1,1,1,1]+run(U,'u')+[0,0]+run(O,'j')+[1,1,1,BLANK],[BLANK],'>'),
           ('B',BL,[0,0,0]+run(Z,'j',3)+[1]+run(U,'u')+[1,1,1,1,BLANK],'>'))
# n = 1 zero digit: K([0];0;b) -> K([b+4;0;0];0;0)
PH['ZONE']=(('B',BL,[0,0,0]+run(U,'b')+[0,0,1,BLANK],'>'),
            ('B',BL,[0]*7+run(U,'b',4)+[1,BLANK],'>'))
PH['ZONE1']=(PH['ZONE'][0],
             ('C',[0,1,1,1,1,BLANK],run(U,'b')+[1,1,1,BLANK],'>'))
PH['CLOOP']=(('C',[0]+run(O,'i')+[BLANK],[1]+run(O,'m')+[BLANK],'>'),
             ('C',[0,1]+run(O,'i')+[BLANK],run(O,'m')+[BLANK],'>'))
PH['CEND']=(('C',[0,1,1,1]+run(U,'u')+[BLANK],[BLANK],'>'),
            ('B',BL,[0,0,0,1]+run(U,'u')+[0,1,1,1,1,BLANK],'>'))
