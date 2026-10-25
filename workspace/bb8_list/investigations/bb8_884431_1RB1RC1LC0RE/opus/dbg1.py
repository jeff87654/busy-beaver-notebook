import sys
from common import *
from rules_r4 import M, G
tree = engine.explore(M, G)
lp = [it for it in tree['items'] if it[0] == 'loop'][0][1]
print('outer start', pl.show(lp['start'])); print('inserts', lp['inserts'])
for r in lp['round']:
    if r[0] == 'loop':
        print('  inner loop on', r[1]['v'], 'start', pl.show(r[1]['start']), 'ins', r[1]['inserts']); print('    result', pl.show(r[1]['result']))
    else:
        print('  ops', [o for o in r[1]][:12])
# reproduce loop_lemma framing
S, v, v2 = lp['start'], lp['v'], lp['v2']
Xb, rema = coqgen.frame_loop(lp, engine, 'j', 'X')
step = engine.subst(Xb, 'j', (('j', 1),), 2)
lhs = engine.subst(Xb, 'j', (('j', 1),), 1)
expect = coqgen.before_w(lhs, lp['inserts'], lambda g: g)
print('step  ', pl.show(step)); print('expect', pl.show(expect))
segs = []
cfg = step
for k in range(4):
    ops, cfg2, how = engine.run_until_stuck(cfg, None, target=expect)
    print(k, how, sum(o[1] for o in ops if o[0]=='steps'), pl.show(cfg2))
    if how != 'stuck': break
    l2 = engine.accelerate(cfg2, 0)
    print('   loop', l2 and l2['v'], l2 and l2['inserts']); 
    if not l2: break
    print('   result', pl.show(l2['result']))
    cfg = l2['result']
