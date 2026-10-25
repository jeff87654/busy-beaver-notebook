"""Longest car chains (consecutive IP zeros) in a .tm decision DAG."""
import sys
from dag import extract
start, tbl, nodes, regidx = extract(sys.argv[1])
def chain(n):
    c = [n]
    while nodes[n][0][0] == 'node':
        n = nodes[n][0][1]; c.append(n)
    return c
res = sorted((chain(n) for n in nodes), key=len, reverse=True)
k = int(sys.argv[2]) if len(sys.argv) > 2 else 6
for c in res[:k]: print(len(c), ' -> '.join(c))
