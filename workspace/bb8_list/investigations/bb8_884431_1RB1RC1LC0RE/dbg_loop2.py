import sys
import rules_r4, coqgen
from rules884 import *
import engine
pl.set_tm(TM)
which = int(sys.argv[1])
name, s, t, prog = rules_r4.pieces()[which]
tree = engine.explore(s, t)
def walk(node, depth=0):
    for it in node['items']:
        if it[0] == 'loop':
            lp = it[1]
            try:
                coqgen.loop_lemma('L%d' % depth, lp, engine, None)
                print('  '*depth, 'loop on', lp['v'], 'OK')
            except Exception as e:
                print('  '*depth, 'loop on', lp['v'], 'FAIL', str(e)[:230])
            walk(it[2], depth+1); walk(it[3], depth+1)
        elif it[0] == 'split':
            walk(it[3], depth+1); walk(it[4], depth+1)
walk(tree)
