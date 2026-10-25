import idle, sys
from blk import follow_blocks
from model import enc, step
from nx import M1,M2
for M in (M1,M2):
    out=follow_blocks(M,'',int(sys.argv[1]),10**9,Q=1)
    # start state: blank, state A -> follow_blocks uses state Q as start; emulate: run from blank with start state A
    print(len(out))
