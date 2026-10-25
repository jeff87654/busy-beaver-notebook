"""python pr.py NAME var=val ...: literal output of the start of EVE[NAME]"""
import sys
from evs_end import *
from probe import next_b
S = EVE[sys.argv[1]][0]
vals = {a.split('=')[0]: int(a.split('=')[1]) for a in sys.argv[2:]}
print(next_b(S, vals))
