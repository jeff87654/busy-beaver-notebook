from common import *
from shapes import *
import mexp
from planner8 import show
s = ('B', [1, 0, 0, 1, run(TB, t=1), 1, 1] + accr(4) + tok(0) + list(Z) + [1, V('l')], [BLANK], '>')
tree = mexp.explore(s, None)
print('\n'.join(mexp.describe(tree)))
print(tree.get('halt'))
