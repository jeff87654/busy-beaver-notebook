"""Static 'tape liveness' of decision-DAG states: a DAG node is entered reading 1 only if its car can
finish normally (the IP bit flips to 1 when the car is done).  Nodes whose car can never finish normally
are only ever entered reading 0.  usage: python liveness.py NAME.tm"""
import sys
from dag import extract
start, tbl, nodes, regidx = extract(sys.argv[1])
memo = {}
def exits(e, stack=()):
    """possible exits of executing edge e: 'N', ('B',k), ('C',k), 'H' (over-approximation)"""
    k = e[0]
    if k == 'op': return {'N'} if e[2] == 'inc' else {'N', ('B', 1)}
    if k == 'break': return {'N'} if e[1] == 0 else {('B', e[1])}
    if k == 'continue': return {('C', e[1])}
    if k == 'halt': return {'H'}
    n = e[1]
    if n in memo: return memo[n]
    if n in stack: return set()          # loop back-edge: contributes via other paths
    car, cdr = nodes[n]; out = set()
    for x in exits(car, stack + (n,)):
        if x == 'N':
            for y in exits(cdr, stack + (n,)):
                if y == 'N' or y == 'H' or y[0] == 'B': out.add(y)
                elif y[1] == 1: pass        # loops back to n: its exits are n's other exits
                else: out.add(('C', y[1] - 1))
        elif x == 'H': out.add('H')
        elif x[0] == 'B': out.add('N' if x[1] == 1 else ('B', x[1] - 1))
        else: out.add(x)
    memo[n] = out; return out
only0 = [n for n in nodes if 'N' not in exits(nodes[n][0])]
print(sys.argv[1], 'DAG nodes', len(nodes), 'entered only reading 0:', len(only0), only0)
fw_single = sorted({s for (s, _) in tbl if s[0].isdigit() and ((s, '0') in tbl) != ((s, '1') in tbl)})
print('framework states with a single row:', fw_single)
