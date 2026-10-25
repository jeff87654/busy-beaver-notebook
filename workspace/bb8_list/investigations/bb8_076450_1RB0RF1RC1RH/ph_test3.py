import planner8 as P, pext
BL=P.BLANK
def run(blk,v): return [('run',tuple(blk),((v,1),))]
V=P.V
PH={}
PH['M1']=(('H', run((1,0,1,0),'m') + [0,1,1,0]*3 + [V('l')], [0,1,0,0,BL], '>'),
          ('F', [0,1,0,1]*3 + [0,0,1,0] + [1,0,1,0]*4 + run((1,0,1,0),'m') + [0,1,1,0] + [V('l')], [1,0,0,0,BL], '>'))
PH['M2']=(('F', run((0,1,0,1),'n') + [0,0,1,0] + [0,1,1,0] + [0,V('l')], [1,0,0,0,BL], '>'),
          ('H', [1,0,1,0]*3 + [0,1,0,1]*7 + run((0,1,0,1),'n') + [0,V('l')], [0,1,0,0,BL], '>'))
import sys
for nm in sys.argv[1:]:
    s,t=PH[nm]
    try:
        sc,e=P.drive(nm, s, t, matchers=[pext.m_concrete, pext.m_sweep], maxev=400, verbose=True)
        print(nm,'OK', sum(o[1] for o in sc if o[0] in ('steps','end')))
    except Exception as ex: print(nm,'EXC',ex)
