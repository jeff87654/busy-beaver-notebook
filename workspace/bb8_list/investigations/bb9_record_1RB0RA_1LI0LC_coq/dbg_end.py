from common import *
import mexp, gen_d2
from planner8 import show, is_run, BLANK
tree = mexp.explore(gen_d2.TARGET, None, splits=0)
end = tree['end']
print(tree.get('halt'), len(tree['items']))
print(show(end))
def count(side):
    c, lin = 0, {}
    for t in side:
        if isinstance(t, int): c += t
        elif is_run(t):
            k = sum(t[1])
            for v, a in t[2]: lin[v] = lin.get(v, 0) + k * a
    return c, lin
q, L, R, mode = end
cl, ll = count(L); cr, lr = count(R)
print('ones: const', cl + cr, 'lin', ll, lr, 'mode', mode)
