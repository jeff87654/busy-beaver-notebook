"""Fast concrete check of a generator item on X' (bytearray sim; compares only when the state equals the goal state).
python vcheck2.py GROUP ITEM a=1,k=0 ...   prints steps or None (and the configs at the goal-state moments if -v)"""
import idle, sys, os
os.environ['ITEM'] = sys.argv[2]
import validate
from common import TM
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_f3_coq\gen')
from tm import Sim
mod = __import__('grp_' + sys.argv[1])
it = {x[0]: x for x in mod.ITEMS}[sys.argv[2]]
verbose = '-v' in sys.argv
def strip(c):
    c = list(c)
    while c and c[-1] == 0: c.pop()
    return c
for spec in [a for a in sys.argv[3:] if a != '-v']:
    vals = {kv.split('=')[0]: int(kv.split('=')[1]) for kv in spec.split(',')}
    q, l, h, r = validate.concretize(it[1], vals)
    gq, gl, gh, gr = validate.concretize(it[2], vals)
    gl, gr = strip(gl), strip(gr)
    word = ''.join(map(str, reversed(strip(l)))) + str(h) + ''.join(map(str, strip(r)))
    sm = Sim(TM, word, head=len(strip(l)), state=q)
    res = None; n = 0
    while n < 50_000_000:
        if sm.q == gq:
            p = sm.pos
            L = strip(sm.t[:p][::-1]); R = strip(sm.t[p + 1:])
            if sm.t[p] == gh and L == gl and R == gr: res = n; break
            if verbose: print('  at', n, sm.q, ''.join(map(str, L[:60][::-1])), sm.t[p], ''.join(map(str, R[:60])))
        if not sm.step(): break
        n += 1
    print(spec, res)
