"""r=2 branch outcome vs t and L (L = 15Q+17).  python r2t.py"""
import idle, subprocess, sys, re
from r2d0 import word
C7 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_0LI---_1LC0RA'
EXE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_c7_coq\tools\c7mf.exe'
for Q in range(0, 13):
    L = 15 * Q + 17
    row = []
    for t in range(3, 14):
        open('tmp_w.txt', 'w').write(word(t, L, 300, 2, 30))
        out = subprocess.run([EXE, C7, 'f:tmp_w.txt', '3e7', 'noh', 'far=100'], capture_output=True, text=True, creationflags=0x40).stdout
        row.append('H' if 'HALT' in out else ('d' if '\nD0' in '\n' + out else '.'))
    print('Q=%2d L=%4d ' % (Q, L) + ' '.join(row), flush=True)
