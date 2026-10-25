"""Run the RM alone for many ops; report IP-space margin assuming gap = 16 + ndecnz, and progress (nextproof)."""
import sys
sys.path.insert(0, 'tools')
from dag import extract, RM, walk
start, tbl, nodes, regidx = extract(sys.argv[1]); nops = int(sys.argv[2])
rm = RM(nodes, 'main().0', len(regidx)); minm = 10**9; worst = None
for i in range(nops):
    leaf, d = walk(nodes, 'main().0', rm.P)
    need = d + (regidx[leaf[1]] + 1 if leaf[0] == 'op' else 0) + 3
    have = 16 + rm.ndecnz
    if have - need < minm: minm = have - need; worst = (i, d, leaf, rm.ndecnz)
    rm.step(regidx)
    if rm.halted: print('HALTED at op', i); break
print('ops', i + 1, 'min margin', minm, 'at', worst, 'regs', rm.regs, 'ndecnz', rm.ndecnz)
