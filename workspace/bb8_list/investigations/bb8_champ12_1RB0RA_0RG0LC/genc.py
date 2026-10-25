"""generic phase generator: genc.py MACHINE(1|2) OUT.v  -- uses phases defined in phdefs.py"""
import sys,os
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import planner8 as pl
from planner8 import drive
from coqgen_util import crossing_lemma, table, cl
from scr2coq import script_to_coq2
import phc
from planner8 import mkrun, V, BLANK
NL=chr(10)
def proof_text(name,start,target,eqs=(),hyps=(),matchers=(),prefix_tac=(),maxev=400,verbose=False):
    script,_=drive(name,start,target,matchers=matchers,maxev=maxev,verbose=verbose)
    if script[-1][0]!='end':
        raise SystemExit('planner did not reach target of %s: %r'%(name,script[-3:]))
    tac=script_to_coq2(script)
    body='Lemma %s : %s.\nProof.\n  intros.\n'%(name,phc.stmt(start,target,eqs,hyps))
    for t in prefix_tac: body+='  '+t+NL
    line='  '
    for t in tac:
        if len(line)+len(t)>100:
            body+=line.rstrip()+NL; line='  '
        line+=t+' '
    body+=line.rstrip()+'\nQed.\n'
    nst=sum(o[1] for o in script if o[0] in ('steps','end'))
    print('  %-8s literal steps %4d, ops %d'%(name,nst,len(script)),file=sys.stderr)
    return body
def crossings():
    return ''.join(crossing_lemma(nm,pl.LEMMAS[nm])+NL for nm in sorted(pl.LEMMAS))
