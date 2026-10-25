"""Cross-check RM (atomic ops) against the TM: at each op start (dispatch with no chain ones) compare path and registers.
Also report the IP-space margin: gap cells available vs needed."""
import sys, re
pass
from tmsim import load
from dag import extract, RM, walk
path = sys.argv[1]; maxsteps = int(sys.argv[2])
start, tbl, nodes, regidx = extract(path)
nreg = len(regidx)
rm = RM(nodes, 'main().0', nreg)
tape = {}; pos = 0; st = start; steps = 0; nops = 0; minmargin = 10**9; mismatch = 0; mingap = 10**9; gapat=None
while steps < maxsteps and not rm.halted:
    if st == 'main().0':
        hi = max(tape)
        ip = ''.join(tape.get(i, '0') for i in range(pos, hi + 1))
        allbits = [int(c) for c in ip]
        leaf, d = walk(nodes, 'main().0', allbits)
        ones = 0
        while allbits[d + ones] == 1: ones += 1
        gap = 0
        while allbits[d + ones + gap] == 0: gap += 1
        if gap < mingap: mingap = gap; gapat = (steps, d, ones, leaf)
        bits = allbits[:d + ones]; ipb = ip[:d + ones]; rf = ip[d + ones:]
        if ones == 0:
            # compare with RM state before executing this op
            rmP = rm.P + [0] * 200
            tmP = bits + [0] * 200
            regs_tm = []
            runs = re.split(r'0+', rf.strip('0'))
            vals = [len(r) - 1 for r in runs if r]
            regs_tm = vals[-nreg:][::-1]  # index 0 = rightmost
            if rmP[:200] != tmP[:200] or regs_tm != rm.regs:
                mismatch += 1
                print('MISMATCH at step', steps, 'op', nops, 'tm', ipb, regs_tm, 'rm', rm.P, rm.regs)
                if mismatch > 5: break
            rm.step(regidx)
            nops += 1
        # margin: need (k+1) ones cells + 3 gap beyond depth d for ops
        need = (regidx[leaf[1]] + 1 if leaf[0] == 'op' else 0) + 3
        margin = (ones + gap) - need
        minmargin = min(minmargin, margin)
    t = tbl.get((st, tape.get(pos, '0')))
    if t is None: print('TM HALT at', steps); break
    w, dd, n = t; tape[pos] = w; pos += 1 if dd == 'R' else -1; st = n; steps += 1
print('min gap', mingap, 'at (step,d,ones,leaf)', gapat)
print('steps', steps, 'ops compared', nops, 'mismatches', mismatch, 'min IP-space margin', minmargin, 'rm halted', rm.halted)
print('final rm regs', rm.regs, 'ndecnz', rm.ndecnz)
