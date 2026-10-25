"""proto1: cross-check a Wade-format TM (with the Q op) against the atomic RM of dag.py (extended with Q).
At each op start (state main().0 with no chain ones) compare the IP path and the WHOLE register file
(every run right of the gap, including boot's deep zero runs and junk run, since Q inserts/deletes registers).
usage: python crosscheck_s.py MACHINE.tm MAXSTEPS"""
import sys, re, os, ctypes
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
try:
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)  # IDLE
except Exception:
    pass
from dag import extract, RM, walk
from collections import Counter
path = sys.argv[1]; maxsteps = int(sys.argv[2])
start, tbl, nodes, regidx = extract(path)
nreg = len(regidx)
rm = None
tape = {}; pos = 0; st = start; steps = 0; nops = 0; minmargin = 10**9; mismatch = 0; mingap = 10**9; gapat = None
leafkinds = Counter(); maxdepthstack = 0
while steps < maxsteps and not (rm and rm.halted):
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
        bits = allbits[:d + ones]; rf = ip[d + ones:]
        if ones == 0:
            runs = re.split(r'0+', rf.strip('0'))
            vals = [len(r) - 1 for r in runs if r][::-1]      # index 0 = rightmost run
            if '00' in rf.strip('0'):
                print('selector/double zero inside RF at op start', steps); mismatch += 1
            if rm is None:
                rm = RM(nodes, 'main().0', nreg); rm.regs = list(vals)
                print('initial RF: %d runs, nonzero at' % len(vals), [(i, v) for i, v in enumerate(vals) if v])
            rmP = rm.P + [0] * 200; tmP = bits + [0] * 200
            if rmP[:200] != tmP[:200] or vals != rm.regs:
                mismatch += 1
                print('MISMATCH at step', steps, 'op', nops, 'tm', bits[:40], vals[:16], 'rm', rm.P[:40], rm.regs[:16])
                if mismatch > 5: break
            lf = rm.step(regidx); nops += 1
            leafkinds[lf[0] if lf[0] != 'op' else lf[2]] += 1
            maxdepthstack = max(maxdepthstack, len(rm.regs))
        need = (regidx[leaf[1]] + 1 if leaf[0] == 'op' else 0) + 3
        margin = (ones + gap) - need
        minmargin = min(minmargin, margin)
    t = tbl.get((st, tape.get(pos, '0')))
    if t is None: print('TM HALT at', steps); break
    w, dd, n = t; tape[pos] = w; pos += 1 if dd == 'R' else -1; st = n; steps += 1
print('min gap', mingap, 'at (step,d,ones,leaf)', gapat)
print('steps', steps, 'ops compared', nops, 'mismatches', mismatch, 'min IP-space margin', minmargin, 'rm halted', rm.halted if rm else None)
print('op kinds', dict(leafkinds), 'Q merges', rm.nmerge, 'Q inserts', rm.ninsert, 'max #runs', maxdepthstack)
print('final rm regs[0:16]', rm.regs[:16], 'ndecnz', rm.ndecnz)
