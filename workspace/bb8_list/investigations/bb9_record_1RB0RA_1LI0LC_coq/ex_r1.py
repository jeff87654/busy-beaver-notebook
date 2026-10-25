import sys, time
sys.path.insert(0, '../../autoproof')
import planner8 as pl
from planner8 import BLANK, V
import engine, coqgen
M11 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_0RG0RE_0LH---'
pl.set_tm(M11)
def run(blk, **cnt):
    return ('run', tuple(blk), tuple(sorted(cnt.items())))
TB = (0, 0, 1, 1, 1, 1, 1, 1)
def left(acc, atok):
    return [1, 0, 0, 1, run(TB, j=1), 1, 1] + acc + [1] + atok + [V('l')]
start = ('B', left([run((0, 1), r=1)], [0, 1] * 3 + [run((0, 1), m=1)]), [BLANK], '>')
target = ('B', left([0, 1] * 4 + [run((0, 1), r=2)], [run((0, 1), m=1)]), [BLANK], '>')
t0 = time.time()
tree = engine.explore(start, target, positive=frozenset(['r']))
print('\n'.join(engine.describe(tree)))
print(time.time() - t0)
