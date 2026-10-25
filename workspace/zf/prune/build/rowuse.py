"""Which (state, symbol) rows of a .tm are ever executed in a long run from the blank tape (evidence for
the combine_states / opposite-tape-liveness merge).  usage: python rowuse.py NAME.tm STEPS"""
import sys
import lowprio
from tmsim import load
start, tbl = load(sys.argv[1]); steps = int(sys.argv[2])
tape = {}; pos = 0; st = start; used = set(); n = 0
while n < steps:
    r = tape.get(pos, '0'); used.add((st, r))
    t = tbl.get((st, r))
    if t is None: print('HALT', st, r); break
    w, d, nx = t; tape[pos] = w; pos += 1 if d == 'R' else -1; st = nx; n += 1
states = sorted({s for s, _ in tbl})
one = {b: [s for s in states if (s, b) in used and (s, '1' if b == '0' else '0') not in used] for b in '01'}
never = [s for s in states if (s, '0') not in used and (s, '1') not in used]
print('states', len(states), 'only-0', len(one['0']), 'only-1', len(one['1']), 'never entered', len(never))
print('only-0:', ' '.join(one['0']))
print('only-1:', ' '.join(one['1']))
print('never:', ' '.join(never))
