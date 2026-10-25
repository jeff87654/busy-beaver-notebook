"""Generate proofs/BB8_m7_1RB0RC.v: machine-level lemmas A, B, C3, C2 (planner) + abstract part."""
import sys, os
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import planner8 as pl
from planner8 import drive, mkrun, V, BLANK
from coqgen_util import crossing_lemma, table, cl
from scr2coq import script_to_coq2
import phc
import ph3
M='1RB0RC_1LC1LF_1RD0LB_1RA1LE_1LG0LC_0LG1LE_0RH1RC_0RA---'
NL=chr(10)
def build(name,start,target):
    script,_=drive(name,start,target,matchers=(),maxev=400,verbose=False)
    assert script[-1][0]=='end', (name,script[-3:])
    tac=script_to_coq2(script)
    body='Lemma %s : %s.\nProof.\n  intros.\n'%(name,phc.stmt(start,target))
    line='  '
    for t in tac:
        if len(line)+len(t)>100:
            body+=line.rstrip()+NL; line='  '
        line+=t+' '
    body+=line.rstrip()+'\nQed.\n'
    return body
def cfgs_AB(T):
    st=[0]+ph3.run('U','i',1)+ph3.run('S','k',1)+ph3.toks(T)+[V('l')]
    tg=[0]+ph3.toks('U')+ph3.run('S','i',0)+ph3.run('U','k',0 if T=='U' else 1)+ph3.toks('SV' if T=='U' else 'S')+[V('l')]
    return ('G',[BLANK],st,'>'),('G',[BLANK],tg,'>')
def cfgs_C(case):
    if case==3:
        st=[0]+ph3.run('U','i',3)+ph3.run('S','k',1)+[BLANK]
        tg=[0]+ph3.run('U','i',1)+ph3.toks('S')+ph3.run('V','k',2)+ph3.toks('S')+[BLANK]
    else:
        st=[0]+ph3.toks('UU')+ph3.run('S','k',1)+[BLANK]
        tg=[0]+ph3.toks('UUS')+ph3.run('V','k',1)+ph3.toks('S')+[BLANK]
    return ('G',[BLANK],st,'>'),('G',[BLANK],tg,'>')
def main(out):
    pl.set_tm(M)
    pl.LEMMAS.clear()
    phases=''
    for nm,(s,t) in [('PA',cfgs_AB('U')),('PB',cfgs_AB('V')),('PC3',cfgs_C(3)),('PC2',cfgs_C(2))]:
        phases+=build(nm,s,t)+NL
    cross=''.join(crossing_lemma(n,pl.LEMMAS[n])+NL for n in sorted(pl.LEMMAS))
    hdr=open(os.path.join(HERE,'head.v.in')).read()
    tail=open(os.path.join(HERE,'tail.v.in')).read()
    txt=hdr.replace('%(table)s',table(M)).replace('%(tm)s',M)+cross+phases+tail
    open(out,'w').write(txt)
    print('wrote',out,len(txt))
if __name__=='__main__': main(sys.argv[1])
