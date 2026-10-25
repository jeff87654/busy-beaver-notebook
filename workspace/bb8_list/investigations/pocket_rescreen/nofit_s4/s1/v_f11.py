import re, sys
from val import *
m = sys.argv[1] if len(sys.argv)>1 else '1RB0RE_1RC0RA_0LD0RH_1LA0LE_1RF0RB_0LG---_0LC1LG_1LD0LE'
tails = ['010001', '0100010010001', '010001001000100010010001', '01000100100010001001000100100010010001', '01000100', '0100010001']
cases = [(x, y, t) for x in (2, 3, 4, 5, 8, 13, 40) for y in (1, 2, 3, 7) for t in tails]
fmt = lambda c: f'E |0 (0001)^{c[0]} (0010)^{c[1]} {c[2]}'
def parse(L, R):
    g = re.fullmatch(r'0((?:0001)*)((?:0010)*)(.*?)0*', R)
    return (len(g.group(1))//4, len(g.group(2))//4, g.group(3).rstrip('0')) if g and not L.strip('0') else ('?',)
check(m, 'E', 'L', cases, fmt, parse, lambda c: (c[0]+2, c[1]-1, c[2].rstrip('0')))
