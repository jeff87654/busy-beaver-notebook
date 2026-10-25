"""tl.py "toks" r [h] [tail] [ncfg] [nsteps] [Qword]: run a family config and print successive rest configs"""
import sys
from fam import *
toks = [int(x) for x in sys.argv[1].split(',') if x != '']
r = int(sys.argv[2]); h = int(sys.argv[3]) if len(sys.argv) > 3 else 8
tail = [int(x) for x in sys.argv[4].split(',')] if len(sys.argv) > 4 and sys.argv[4] else [1,1]
n = int(sys.argv[5]) if len(sys.argv) > 5 else 6
N = int(float(sys.argv[6])) if len(sys.argv) > 6 else 10**8
Q = sys.argv[7] if len(sys.argv) > 7 else ''
w = word_of(Q, toks, r, h, tail)
for c in run(w, N, n): print(fmt(c))
