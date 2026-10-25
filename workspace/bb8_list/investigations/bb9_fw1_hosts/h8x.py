"""h8x.py: H8 marker-contact test. Plant every binary word X (len 1..7, starting and ending with 1) at gap g = 1..3 beyond
the round-0 reset word of H8 and run the MODE-1 chain (6 rounds, b1 = 3). Report outcome classes (halt round/slot, or none)."""
import idle, subprocess, itertools, collections, re
M = '1RB1RG_0LC1LH_1LD1RC_---0LE_0RF0LA_0RA1LH_1RA0RC_1RA1LF'; W0 = '1101010111110101011'
import os
EXE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hpc.exe')
C = collections.Counter(); hits = []
for L in range(1, 8):
    for bits in itertools.product('01', repeat=L):
        X = ''.join(bits)
        if X[0] != '1' or X[-1] != '1': continue
        for g in (1, 2, 3):
            w = X + '0' * g + W0
            o = subprocess.run([EXE, M, 'R', 'C', '10', '11', '11', '0', '1', '0', w, str(len(w)), 'C', '3', '6', '20000000', '6', '2', '1'],
                               capture_output=True, text=True, creationflags=0x40).stdout
            h = re.search(r'R(\d) HALT \d+ state (\w) read (\d)', o); t = re.search(r'R(\d) TIMEOUT', o)
            k = f'H{h[1]}:{h[2]}{h[3]}' if h else (f'T{t[1]}' if t else 'none')
            C[k] += 1
            if k != 'none': hits.append((X, g, k))
print(C)
for x in hits[:60]: print(*x)
