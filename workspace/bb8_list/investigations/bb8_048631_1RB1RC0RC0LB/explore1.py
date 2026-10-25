from lit import *
import sys
# print config whenever head reaches new leftmost or rightmost
state = {'lo':0,'hi':0}
def cb(i, tape, pos, q):
    if pos < state['lo'] or pos > state['hi']:
        state['lo'] = min(state['lo'], pos); state['hi'] = max(state['hi'], pos)
        if i < 200000:
            print(i, 'L' if pos==state['lo'] else 'R', show(tape,pos,q)[:300])
r = run(int(sys.argv[1]), cb=cb)
print(r[0], r[1])
