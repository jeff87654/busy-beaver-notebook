# nmsweep.py: literal near-miss (A1E1) counts for H1 exhaustion templates T1/T2/T3, b = 1..120, 2e8 steps each (1 Idle core)
import subprocess, os
D = os.path.dirname(os.path.abspath(__file__)); EXE = os.path.join(D, 'src', 'nm.exe')
M = '1RB1RE_1RC1RA_0LD1LE_1RE1LE_0RG0RF_---0LG_1LC1RA'
T = {'T1': ('1010', 'E'), 'T2': ('11', 'E'), 'T3': ('10', 'C')}
out = open(os.path.join(D, 'nm_H1.tsv'), 'w')
for name, (pre, q) in T.items():
    for b in range(1, 121):
        w = pre + '01' * b + '0010'
        p = subprocess.Popen([EXE, M, w, '-1', q, '200000000', 'A1E1'], stdout=subprocess.PIPE, text=True, creationflags=0x40)
        open(os.path.join(D, 'pids.txt'), 'a').write(f'{p.pid} nm.exe {name} {b}\n')
        out.write(f'{name}\t{b}\t{p.communicate()[0].strip()}\n'); out.flush()
