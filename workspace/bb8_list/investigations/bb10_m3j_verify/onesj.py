"""ones at halt for chosen fakes (B fixed), varying one fake at a time; prints the halting tape compressed."""
import sys
import osim
from chain_j import run_chain
from fw import *
B = int(sys.argv[1]); base = [int(x) for x in sys.argv[2].split(',')]
sig, kind, ones0, hq = run_chain(B, base)
print('base', base, kind, ones0)
for i in range(6):
    fk = list(base); fk[i] += 120
    sig, kind, ones, hq = run_chain(B, fk)
    print('F%d +120:' % (i + 1), kind, ones, 'delta', ones - ones0, flush=True)
