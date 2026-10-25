import re, sys
from val import *
m = sys.argv[1]
cases = [(a, b) for a in range(2, 40) for b in range(0, 9)] + [(a, b) for a in (100, 257, 600) for b in (0, 1, 2, 3, 50, 51)]
fmt = lambda c: f'F |0 1^{c[0]} 0 1^{c[1]}' if c[1] else f'F |0 1^{c[0]} 0'
def parse(L, R):
    mm = re.fullmatch(r'0(1+)0(1*)0*', R)
    return (len(mm.group(1)), len(mm.group(2))) if mm and L.strip('0') == '' else ('?', R[:40])
def rule(c):
    a, b = c
    if b >= 3: return (2*a+8, b-2)
    if b == 2: return 'H'
    return (2, 2*a+5) if b == 1 else (2, 2*a+4)
check(m, 'F', 'L', cases, fmt, parse, rule)
