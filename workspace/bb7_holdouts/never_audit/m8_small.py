import sys, idle_guard, subprocess
from coding import ChampCoding
from sym import SYMSIM
C = ChampCoding(); M8 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_1RG---'
for n0 in (11, 1, 2):
    for X in range(1, 26):
        tp = C.encode([0] * n0 + [X], [0, 3, 0, 1], 0, 'B')
        p = subprocess.run([SYMSIM, 'run', '--noch', '--nokt', '--budget', '200000000', '--tlimit', '40'], input='%s B %s\n' % (M8, tp), capture_output=True, text=True)
        l = [x for x in p.stdout.splitlines() if x.startswith('R ')]
        print(n0, X, l[0][:160] if l else p.stdout[:100], flush=True)
