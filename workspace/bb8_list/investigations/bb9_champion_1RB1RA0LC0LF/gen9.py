"""Generate planner scripts for the BB(9) champion phases (original orientation) -> phases.v fragment."""
import sys
import planner9 as pl
from planner9 import mkrun, V, BLANK, drive
from coqgen_util import script_to_coq, crossing_lemma

ONE=(1,)
def K(R): return ('D',[BLANK],R,'<')
PH=[]
def phase(name, stmt, start, target, progress=True):
    pl.LEMMAS.clear()
    script, cfg = drive(name, start, target, matchers=(), maxev=300, verbose=False)
    if script[-1][0] != 'end':
        raise SystemExit('phase %s did not reach target: %r' % (name, script[-3:]))
    body = script_to_coq(script, progress)
    PH.append((name, stmt, body, dict(pl.LEMMAS)))

b={'b':1}; a={'a':1}; y={'y':1}; r={'r':1}; s_={'s':1}; m={'m':1}; i_={'i':1}
phase('R1', 'forall b a l, const 0 <{{D}} (1 >> [1]^^b *> 0 >> 1 >> [1]^^a *> l) -->+ const 0 <{{D}} (1 >> 1 >> 1 >> 1 >> [1]^^b *> 0 >> [1]^^a *> l)',
  K([1]+mkrun(ONE,b)+[0,1]+mkrun(ONE,a)+[V('l')]),
  K([1]+mkrun(ONE,b,3)+[0]+mkrun(ONE,a)+[V('l')]))
phase('R2', 'forall b y t, const 0 <{{D}} (1 >> [1]^^b *> 0 >> 0 >> 1 >> [1]^^y *> t) -->+ const 0 <{{D}} (1 >> 1 >> 0 >> 1 >> 1 >> [1]^^b *> 0 >> [1]^^y *> t)',
  K([1]+mkrun(ONE,b)+[0,0,1]+mkrun(ONE,y)+[V('t')]),
  K([1,1,0,1,1]+mkrun(ONE,b)+[0]+mkrun(ONE,y)+[V('t')]))
phase('ENTRY', 'forall b w, const 0 <{{D}} (1 >> [1]^^b *> 0 >> w) -->+ ([1]^^b *> 1 >> 1 >> const 0) {{A}}> (0 >> w)',
  K([1]+mkrun(ONE,b)+[0,V('w')]),
  ('A',mkrun(ONE,b)+[1,1,BLANK],[0,V('w')],'>'))
phase('LOOP', 'forall r Y z, (1 >> 1 >> [1]^^r *> 0 >> Y) {{A}}> (0 >> 0 >> z) -->+ ([1]^^r *> 0 >> 1 >> 1 >> 0 >> Y) {{A}}> (0 >> z)',
  ('A',[1,1]+mkrun(ONE,r)+[0,V('Y')],[0,0,V('z')],'>'),
  ('A',mkrun(ONE,r)+[0,1,1,0,V('Y')],[0,V('z')],'>'))
phase('FINAL', 'forall s m y t, ([1]^^s *> 0 >> 1 >> 1 >> 0 >> 1 >> 1 >> [0;1;1]^^m *> const 0) {{A}}> (0 >> 1 >> [1]^^y *> t) -->+ const 0 <{{D}} (1 >> [1;0;1]^^m *> 1 >> 0 >> 1 >> 1 >> 0 >> 1 >> [1]^^s *> 1 >> 0 >> [1]^^y *> t)',
  ('A',mkrun(ONE,s_)+mkrun((0,1,1),m,2)+[BLANK],[0,1]+mkrun(ONE,y)+[V('t')],'>'),
  K([1]+mkrun((1,0,1),m)+[1,0,1,1,0,1]+mkrun(ONE,s_)+[1,0]+mkrun(ONE,y)+[V('t')]))
phase('R4E', 'forall i, ([0;1;1]^^i *> const 0) {{A}}> const 0 -->+ const 0 <{{D}} (1 >> [0;1;0]^^i *> 0 >> 1 >> 1 >> const 0)',
  ('A',mkrun((0,1,1),i_)+[BLANK],[BLANK],'>'),
  K([1]+mkrun((0,1,0),i_)+[0,1,1,BLANK]))

def emit(f):
    seen = {}
    for name, stmt, body, lem in PH:
        for k, v in lem.items():
            seen[k] = v
    for k, v in seen.items():
        f.write(crossing_lemma(k, v) + '\n')
    for name, stmt, body, lem in PH:
        f.write('Lemma %s : %s.\nProof.\n  intros.\n' % (name, stmt))
        for line in body: f.write('  ' + line + '\n')
        f.write('Qed.\n\n')

if __name__ == '__main__':
    with open('phases.v','w') as f: emit(f)
    print(open('phases.v').read())
