# spec2cells.py TAPEFILE n : symsim TAPE line with X0 := n  ->  "cells headindex state"
import sys, re
line = open(sys.argv[1]).read().split('\n')[0].split(' ', 1)[1]; n = int(sys.argv[2])
s = re.sub(r'\{([^}]*)\}', lambda g: str(eval(g.group(1).replace('X0', str(n)))), line).split()
cells = ''; head = None; q = 'A'
for t in s:
    if len(t) == 2 and t[1] == '>': head = len(cells); q = t[0]; continue
    if len(t) == 2 and t[0] == '<': head = len(cells) - 1; q = t[1]; continue
    w, _, k = t.partition('^'); cells += w * (int(k) if k else 1)
if head >= len(cells): cells += '0'
print(cells, head, q)
