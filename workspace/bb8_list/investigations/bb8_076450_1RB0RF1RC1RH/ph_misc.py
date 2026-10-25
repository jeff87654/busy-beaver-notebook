import sys
import planner8 as P, pext, loops
BL=P.BLANK
def run(blk,v): return [('run',tuple(blk),((v,1),))]
V=P.V
P1=[0,0,0,1,0,1,0,1,1]            # "1 10101000" reversed
P2=[0,0,0,1,0,1,0,1,0,1,0,0,1,0,1,1]  # "11010010 10101000" reversed
PH={}
PH['Start']=(('F',[0,1,1,0]*5+[0,V('l')],[1,1,0,1,BL],'>'), ('H',[1,0,1,0]*279+[0,V('l')],[0,1,0,0,BL],'>'))
PH['End1']=(('H',run((1,0,1,0),'m')+P1+[BL],[0,1,0,0,BL],'>'), ('F',[0,1,1,0]+run((0,1,1,0),'m')+P2+[BL],[1,1,0,1,BL],'>'))
PH['Init']=(('A',[BL],[BL],'>'), ('F',[0,1,1,0]*11+P1+[BL],[1,1,0,1,BL],'>'))
for nm in sys.argv[1:]:
    s,t=PH[nm]
    try:
        sc,e=P.drive(nm, s, t, matchers=[loops.m_TA, loops.m_TB, pext.m_concrete, pext.m_sweep], maxev=3000, verbose=('-v' in sys.argv))
        print(nm,'OK literal steps', sum(o[1] for o in sc if o[0] in ('steps','end')), 'ops', len(sc), 'loops', [o[1] for o in sc if o[0]=='lemma' and isinstance(o[1],tuple)])
    except Exception as ex: print(nm,'EXC',ex)
